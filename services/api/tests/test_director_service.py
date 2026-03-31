import asyncio
from pathlib import Path

from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.director.policies.member_director_hybrid import MemberDirectorHybridPolicy
from app.director.service import DirectorControlService, DirectorPanelService
from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.relationship.service import RelationshipService
from app.social.interaction_service import MomentInteractionService
from app.social.models import CreateMomentCommentRequest, CreateMomentLikeRequest, CreateMomentRequest
from app.social.service import SocialService
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


def test_director_panel_applies_delay_rules_to_private_chat_plans_and_relationships(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'director-delay.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        runtime = WorldRuntimeService(
            thinking_engine=StateDrivenThinkingEngine(),
            default_speed_multiplier=60.0,
        )
        runtime.bootstrap_sample_world()

        social_service = SocialService(database, world_id=runtime.world_id)
        relationship_service = RelationshipService(database, world_id=runtime.world_id)
        world_persistence = WorldPersistenceService(database)
        interaction_service = MomentInteractionService(
            social_service=social_service,
            relationship_service=relationship_service,
            world_runtime=runtime,
            world_persistence=world_persistence,
        )
        await social_service.ensure_defaults()
        await relationship_service.ensure_defaults(characters=runtime.list_characters())

        now = runtime.clock.snapshot().now
        await social_service.post_private_message(
            sender_id="char-001",
            target_id="char-002",
            content="先发一条私聊测试延迟可见",
            created_at=now,
        )
        created_moment = await social_service.create_moment(
            CreateMomentRequest(
                sender_id="char-001",
                content="给导演视角补一条互动样本",
                mentions=[],
                created_at=now,
            )
        )
        await interaction_service.create_comment(
            moment_id=created_moment.id,
            request=CreateMomentCommentRequest(
                sender_id="char-002",
                content="我先补一条评论",
                created_at=now,
            ),
        )
        await interaction_service.create_like(
            moment_id=created_moment.id,
            request=CreateMomentLikeRequest(
                sender_id="char-002",
                created_at=now,
            ),
        )
        await relationship_service.apply_social_interaction(
            source_character_id="char-001",
            target_character_ids=["char-002"],
            interaction_kind="private_message",
        )
        control_service = DirectorControlService(
            world_runtime=runtime,
            world_persistence=world_persistence,
            permission_policy=MemberDirectorHybridPolicy(director_delay_seconds=300),
        )
        await control_service.pause_world()

        service = DirectorPanelService(
            world_runtime=runtime,
            social_service=social_service,
            moment_interaction_service=interaction_service,
            relationship_service=relationship_service,
            permission_policy=MemberDirectorHybridPolicy(director_delay_seconds=300),
            director_visibility_delay_seconds=300,
        )

        hidden_panel = await service.get_panel_state()
        private_preview = next(
            item for item in hidden_panel.conversations if item.conversation_type == "private"
        )
        assert private_preview.last_message_preview is None
        assert private_preview.last_message_at is None
        assert all(item.current_plan_summary == "导演视角延迟可见" for item in hidden_panel.characters)
        assert hidden_panel.relationships == []
        assert hidden_panel.moment_interactions == []
        assert any(
            log.summary == "Director paused the world runtime."
            for log in hidden_panel.recent_logs
        )
        assert all(log.kind != "moment_interaction_recorded" for log in hidden_panel.recent_logs)

        await control_service.resume_world()
        runtime.clock.tick(301)
        visible_panel = await service.get_panel_state()
        private_preview = next(
            item for item in visible_panel.conversations if item.conversation_type == "private"
        )
        assert private_preview.last_message_preview is not None
        assert any(item.current_plan_summary != "导演视角延迟可见" for item in visible_panel.characters)
        assert visible_panel.relationships
        assert len(visible_panel.moment_interactions) == 2
        assert {item.interaction_type for item in visible_panel.moment_interactions} == {
            "comment",
            "like",
        }
        assert any(log.kind == "moment_interaction_recorded" for log in visible_panel.recent_logs)

        await database.engine.dispose()

    asyncio.run(scenario())
