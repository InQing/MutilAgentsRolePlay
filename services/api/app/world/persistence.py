from app.infra.db.repositories import (
    AsyncCharacterRepository,
    AsyncConversationRepository,
    AsyncPlanRepository,
    AsyncSchedulerRepository,
    AsyncWorldEventRepository,
    AsyncWorldRepository,
)
from app.infra.db.session import DatabaseManager
from app.world.service import WorldRuntimeService


class WorldPersistenceService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    async def bootstrap_or_load(self, runtime: WorldRuntimeService) -> None:
        async with self.database.session_factory() as session:
            world_repo = AsyncWorldRepository(session)
            character_repo = AsyncCharacterRepository(session)
            event_repo = AsyncWorldEventRepository(session)
            plan_repo = AsyncPlanRepository(session)
            scheduler_repo = AsyncSchedulerRepository(session)
            conversation_repo = AsyncConversationRepository(session)

            clock_state = await world_repo.get(runtime.world_id)
            if clock_state is None:
                await self.persist_runtime(runtime)
                return

            characters = await character_repo.list_for_world(world_id=runtime.world_id)
            plans = await plan_repo.list_for_world(world_id=runtime.world_id)
            tasks = await scheduler_repo.list_for_world(world_id=runtime.world_id)
            events = await event_repo.list_recent_for_world(world_id=runtime.world_id, limit=20)
            runtime.replace_runtime_state(
                clock_state=clock_state,
                characters=characters,
                plans=plans,
                tasks=tasks,
                events=events,
            )
            await conversation_repo.ensure_defaults(world_id=runtime.world_id)
            await session.commit()

    async def persist_runtime(self, runtime: WorldRuntimeService) -> None:
        async with self.database.session_factory() as session:
            async with session.begin():
                world_repo = AsyncWorldRepository(session)
                character_repo = AsyncCharacterRepository(session)
                event_repo = AsyncWorldEventRepository(session)
                plan_repo = AsyncPlanRepository(session)
                scheduler_repo = AsyncSchedulerRepository(session)
                conversation_repo = AsyncConversationRepository(session)

                await world_repo.upsert(
                    world_id=runtime.world_id,
                    clock=runtime.clock.snapshot(),
                )
                await character_repo.replace_for_world(
                    world_id=runtime.world_id,
                    characters=runtime.character_repository.list_all(),
                )
                await plan_repo.replace_for_world(
                    world_id=runtime.world_id,
                    plans=runtime.list_plans(),
                )
                await scheduler_repo.replace_for_world(
                    world_id=runtime.world_id,
                    tasks=runtime.get_pending_tasks(),
                )
                await event_repo.append_many(runtime.get_recent_events(limit=50))
                await conversation_repo.ensure_defaults(world_id=runtime.world_id)
