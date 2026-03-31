import asyncio
from pathlib import Path

from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.relationship.service import RelationshipService
from app.social.interaction_service import MomentInteractionService
from app.social.models import CreateMomentCommentRequest, CreateMomentLikeRequest
from app.social.service import SocialService
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


def test_moment_interaction_service_creates_comment_like_and_world_events(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'moment-interactions.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        runtime = WorldRuntimeService(
            thinking_engine=StateDrivenThinkingEngine(),
            default_speed_multiplier=60.0,
        )
        runtime.bootstrap_sample_world()

        social_service = SocialService(database, world_id=runtime.world_id)
        relationship_service = RelationshipService(database, world_id=runtime.world_id)
        persistence_service = WorldPersistenceService(database)
        interaction_service = MomentInteractionService(
            social_service=social_service,
            relationship_service=relationship_service,
            world_runtime=runtime,
            world_persistence=persistence_service,
        )

        await social_service.ensure_defaults()
        await relationship_service.ensure_defaults(characters=runtime.list_characters())

        moment = await social_service.post_moment(
            sender_id="char-001",
            content="今天的朋友圈先发这一条。",
        )
        comment = await interaction_service.create_comment(
            moment_id=moment.id,
            request=CreateMomentCommentRequest(
                sender_id="char-002",
                content="我先来评论一下",
            ),
        )
        first_like = await interaction_service.create_like(
            moment_id=moment.id,
            request=CreateMomentLikeRequest(sender_id="char-002"),
        )
        second_like = await interaction_service.create_like(
            moment_id=moment.id,
            request=CreateMomentLikeRequest(sender_id="char-002"),
        )

        interactions = await interaction_service.list_interactions(moment_id=moment.id)
        relationships = await relationship_service.list_relationships()
        relationship_lookup = {
            (edge.source_character_id, edge.target_character_id): edge
            for edge in relationships
        }

        assert comment.interaction_type == "comment"
        assert first_like.interaction_type == "like"
        assert first_like.id == second_like.id
        assert len(interactions) == 2
        assert [item.interaction_type for item in interactions] == ["comment", "like"]
        assert relationship_lookup[("char-002", "char-001")].affinity == 0.065
        assert relationship_lookup[("char-002", "char-001")].labels[0] == "recent_moment_reply"
        assert relationship_lookup[("char-002", "char-001")].labels[-1] == "recent_moment_reaction"
        assert any(
            event.kind.value == "moment_interaction_recorded"
            for event in runtime.get_recent_events(limit=10)
        )

        await database.engine.dispose()

    asyncio.run(scenario())
