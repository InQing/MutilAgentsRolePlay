import asyncio
from pathlib import Path

from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.character.models import (
    CharacterProfile,
    CreateCharacterRequest,
    UpdateCharacterRequest,
)
from app.character.service import CharacterManagementService
from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.relationship.service import RelationshipService
from app.social.service import SocialService
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


def _build_runtime_services(database: DatabaseManager):
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()
    persistence = WorldPersistenceService(database)
    relationship_service = RelationshipService(
        database,
        world_id=runtime.world_id,
    )
    social_service = SocialService(
        database,
        world_id=runtime.world_id,
    )
    management_service = CharacterManagementService(
        world_runtime=runtime,
        world_persistence=persistence,
        relationship_service=relationship_service,
    )
    return runtime, persistence, relationship_service, social_service, management_service


def test_character_management_service_updates_existing_character_and_restores_profile(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'character-update.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        runtime, persistence, relationship_service, _, management_service = _build_runtime_services(
            database
        )
        await relationship_service.ensure_defaults(characters=runtime.list_characters())
        await persistence.persist_runtime(runtime)

        updated = await management_service.update_character(
            character_id="char-001",
            request=UpdateCharacterRequest(
                display_name="林澈-已调整",
                profile=CharacterProfile(
                    identity_and_background="正在学习如何稳定经营多角色社交场景。",
                    personality="主动、敏锐、愿意快速接住话题。",
                    speaking_style="热络、带一点组织者语气。",
                    appearance_and_presence="给人轻快、存在感强的印象。",
                    additional_notes="这次要更明显地像主持人。",
                ),
                current_plan_summary="重新梳理今天的聚会安排",
                emotion_state="energized",
                social_drive=0.91,
                interrupt_threshold=0.38,
            ),
        )

        assert updated.display_name == "林澈-已调整"
        assert updated.profile.speaking_style == "热络、带一点组织者语气。"
        runtime_character = runtime.get_character("char-001")
        assert runtime_character is not None
        assert runtime_character.current_plan_summary == "重新梳理今天的聚会安排"
        active_plan = runtime.plan_repository.get_active_for_character(character_id="char-001")
        assert active_plan is not None
        assert active_plan.summary == "重新梳理今天的聚会安排"

        restored_runtime = WorldRuntimeService(
            thinking_engine=StateDrivenThinkingEngine(),
            default_speed_multiplier=60.0,
        )
        restored_runtime.bootstrap_sample_world()
        await persistence.bootstrap_or_load(restored_runtime)
        restored_character = restored_runtime.get_character("char-001")
        assert restored_character is not None
        assert restored_character.display_name == "林澈-已调整"
        assert restored_character.profile.additional_notes == "这次要更明显地像主持人。"
        restored_plan = restored_runtime.plan_repository.get_active_for_character(character_id="char-001")
        assert restored_plan is not None
        assert restored_plan.summary == "重新梳理今天的聚会安排"

        await database.engine.dispose()

    asyncio.run(scenario())


def test_character_management_service_creates_and_deletes_character_without_losing_history(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'character-create-delete.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        runtime, persistence, relationship_service, social_service, management_service = _build_runtime_services(
            database
        )
        await social_service.ensure_defaults()
        await relationship_service.ensure_defaults(characters=runtime.list_characters())
        await persistence.persist_runtime(runtime)

        created = await management_service.create_character(
            request=CreateCharacterRequest(
                display_name="苏见",
                profile=CharacterProfile(
                    identity_and_background="新加入这个世界的自由撰稿人，经常在观察人与气氛。",
                    personality="温和、谨慎、会先判断场合再发言。",
                    speaking_style="句子偏柔和，喜欢先留余地。",
                    appearance_and_presence="外在安静，不抢镜，但容易让人记住。",
                    additional_notes="适合担任慢热但稳定的观察者角色。",
                ),
                current_plan_summary="先熟悉群聊里每个人的节奏",
                emotion_state="curious",
                social_drive=0.63,
                interrupt_threshold=0.52,
            )
        )

        assert runtime.get_character(created.id) is not None
        assert runtime.plan_repository.get_active_for_character(character_id=created.id) is not None
        assert any(
            task.payload.get("character_id") == created.id
            for task in runtime.get_pending_tasks()
        )

        relationships = await relationship_service.list_relationships()
        assert len(
            [
                item
                for item in relationships
                if created.id in {item.source_character_id, item.target_character_id}
            ]
        ) == 4

        await social_service.post_group_message(
            sender_id=created.id,
            content="先补一条消息，确认删除角色后历史仍然保留。",
        )
        deleted = await management_service.delete_character(character_id=created.id)
        assert deleted.character_id == created.id
        assert runtime.get_character(created.id) is None
        assert runtime.plan_repository.get_active_for_character(character_id=created.id) is None
        assert all(
            task.payload.get("character_id") != created.id
            for task in runtime.get_pending_tasks()
        )

        remaining_relationships = await relationship_service.list_relationships()
        assert all(
            created.id not in {item.source_character_id, item.target_character_id}
            for item in remaining_relationships
        )

        listed_messages = await social_service.list_messages(conversation_id="conv-general")
        assert any(message.sender_id == created.id for message in listed_messages)

        await database.engine.dispose()

    asyncio.run(scenario())
