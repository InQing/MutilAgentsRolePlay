import asyncio
from pathlib import Path

from app.character.models import CharacterState
from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.relationship.service import RelationshipService


def test_relationship_service_creates_default_edges_for_each_character_pair(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'relationships.db'}")
    characters = [
        CharacterState(
            id="char-001",
            display_name="林澈",
            current_plan_summary="准备群聊",
            emotion_state="curious",
            social_drive=0.8,
            interrupt_threshold=0.4,
        ),
        CharacterState(
            id="char-002",
            display_name="许遥",
            current_plan_summary="处理工作",
            emotion_state="focused",
            social_drive=0.3,
            interrupt_threshold=0.7,
        ),
        CharacterState(
            id="char-003",
            display_name="周宁",
            current_plan_summary="整理朋友圈",
            emotion_state="relaxed",
            social_drive=0.6,
            interrupt_threshold=0.5,
        ),
    ]

    async def scenario() -> None:
        await initialize_database(database)
        service = RelationshipService(database, world_id="test-world")

        await service.ensure_defaults(characters=characters)
        relationships = await service.list_relationships()

        assert len(relationships) == 6
        assert all(edge.affinity == 0.0 for edge in relationships)
        assert {
            (edge.source_character_id, edge.target_character_id)
            for edge in relationships
        } == {
            ("char-001", "char-002"),
            ("char-001", "char-003"),
            ("char-002", "char-001"),
            ("char-002", "char-003"),
            ("char-003", "char-001"),
            ("char-003", "char-002"),
        }

        await database.engine.dispose()

    asyncio.run(scenario())


def test_relationship_service_applies_explainable_bidirectional_deltas(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'relationships.db'}")
    characters = [
        CharacterState(
            id="char-001",
            display_name="林澈",
            current_plan_summary="准备群聊",
            emotion_state="curious",
            social_drive=0.8,
            interrupt_threshold=0.4,
        ),
        CharacterState(
            id="char-002",
            display_name="许遥",
            current_plan_summary="处理工作",
            emotion_state="focused",
            social_drive=0.3,
            interrupt_threshold=0.7,
        ),
    ]

    async def scenario() -> None:
        await initialize_database(database)
        service = RelationshipService(database, world_id="test-world")
        await service.ensure_defaults(characters=characters)

        updated_relationships = await service.apply_social_interaction(
            source_character_id="char-001",
            target_character_ids=["char-002", "char-002", "char-001"],
            interaction_kind="private_message",
        )

        assert len(updated_relationships) == 2
        edge_lookup = {
            (edge.source_character_id, edge.target_character_id): edge
            for edge in updated_relationships
        }
        assert edge_lookup[("char-001", "char-002")].affinity == 0.08
        assert edge_lookup[("char-002", "char-001")].affinity == 0.04
        assert edge_lookup[("char-001", "char-002")].labels == ["recent_private_contact"]
        assert edge_lookup[("char-002", "char-001")].labels == ["recent_private_contact"]

        persisted_relationships = await service.list_relationships()
        persisted_lookup = {
            (edge.source_character_id, edge.target_character_id): edge
            for edge in persisted_relationships
        }
        assert persisted_lookup[("char-001", "char-002")].affinity == 0.08
        assert persisted_lookup[("char-002", "char-001")].affinity == 0.04

        await database.engine.dispose()

    asyncio.run(scenario())


def test_relationship_service_clamps_affinity_and_supports_moment_comment_rules(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'relationships.db'}")
    characters = [
        CharacterState(
            id="char-001",
            display_name="林澈",
            current_plan_summary="准备群聊",
            emotion_state="curious",
            social_drive=0.8,
            interrupt_threshold=0.4,
        ),
        CharacterState(
            id="char-002",
            display_name="许遥",
            current_plan_summary="处理工作",
            emotion_state="focused",
            social_drive=0.3,
            interrupt_threshold=0.7,
        ),
    ]

    async def scenario() -> None:
        await initialize_database(database)
        service = RelationshipService(database, world_id="test-world")
        await service.ensure_defaults(characters=characters)

        for _ in range(30):
            await service.apply_social_interaction(
                source_character_id="char-001",
                target_character_ids=["char-002"],
                interaction_kind="moment_comment",
            )

        relationships = await service.list_relationships()
        relationship_lookup = {
            (edge.source_character_id, edge.target_character_id): edge
            for edge in relationships
        }
        assert relationship_lookup[("char-001", "char-002")].affinity == 1.0
        assert relationship_lookup[("char-002", "char-001")].affinity == 0.75
        assert relationship_lookup[("char-001", "char-002")].labels[-1] == "recent_moment_reply"
        assert relationship_lookup[("char-002", "char-001")].labels[-1] == "recent_moment_reply"

        await database.engine.dispose()

    asyncio.run(scenario())
