import asyncio
from pathlib import Path

from app.agent_runtime.executor import AutonomousActionExecutor
from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.social.service import SocialService
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


def test_world_persistence_can_restore_clock_events_and_pending_tasks(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'restore.db'}")

    async def scenario() -> None:
        await initialize_database(database)

        runtime = WorldRuntimeService(
            thinking_engine=StateDrivenThinkingEngine(),
            default_speed_multiplier=60.0,
        )
        runtime.bootstrap_sample_world()
        social_service = SocialService(database, world_id=runtime.world_id)
        executor = AutonomousActionExecutor(runtime=runtime, social_gateway=social_service)
        persistence = WorldPersistenceService(database)

        await social_service.ensure_defaults()
        due_tasks, _ = runtime.advance(seconds=700)
        await executor.execute_due_tasks(tasks=due_tasks)
        await persistence.persist_runtime(runtime)

        restored_runtime = WorldRuntimeService(
            thinking_engine=StateDrivenThinkingEngine(),
            default_speed_multiplier=60.0,
        )
        restored_runtime.bootstrap_sample_world()
        restored_persistence = WorldPersistenceService(database)
        await restored_persistence.bootstrap_or_load(restored_runtime)

        restored_state = restored_runtime.get_world_state()
        assert restored_state.recent_events
        assert any("action_executed" in item or "wrote a new message" in item for item in restored_state.recent_events)
        assert len(restored_state.pending_tasks) >= 1
        assert len(restored_state.active_characters) == 2

        await database.engine.dispose()

    asyncio.run(scenario())

