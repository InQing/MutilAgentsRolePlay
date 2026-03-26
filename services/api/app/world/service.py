from datetime import datetime, timedelta, timezone

from app.agent_runtime.thinking.base import ThinkingEngine
from app.character.models import CharacterState
from app.infra.db.repositories import (
    CharacterRepository,
    SchedulerRepository,
    WorldEventRepository,
)
from app.world.clock import WorldClock
from app.world.event_bus import WorldEventBus
from app.world.events import RuntimeTask, WorldEvent, WorldEventKind
from app.world.models import WorldState
from app.world.scheduler import WorldScheduler


class WorldRuntimeService:
    def __init__(
        self,
        *,
        thinking_engine: ThinkingEngine,
        default_speed_multiplier: float,
    ) -> None:
        self.thinking_engine = thinking_engine
        self.clock = WorldClock(speed_multiplier=default_speed_multiplier)
        self.event_bus = WorldEventBus()
        self.scheduler = WorldScheduler()
        self.character_repository = CharacterRepository()
        self.event_repository = WorldEventRepository()
        self.scheduler_repository = SchedulerRepository()
        self.world_id = "local-prototype"

    def bootstrap_sample_world(self) -> None:
        characters = [
            CharacterState(
                id="char-001",
                display_name="林澈",
                current_plan_summary="整理今天的群聊动态并准备晚上的聚会",
                emotion_state="curious",
                social_drive=0.82,
                interrupt_threshold=0.45,
            ),
            CharacterState(
                id="char-002",
                display_name="许遥",
                current_plan_summary="专注完成工作，在必要时才回复消息",
                emotion_state="focused",
                social_drive=0.34,
                interrupt_threshold=0.72,
            ),
        ]
        self.character_repository.save_many(characters)

        now = datetime.now(timezone.utc)
        tasks = [
            RuntimeTask(
                world_id=self.world_id,
                task_type="character_plan_tick",
                run_at=now + timedelta(minutes=10),
                payload={"character_id": "char-001", "intent": "check_group_chat"},
                priority=1,
            ),
            RuntimeTask(
                world_id=self.world_id,
                task_type="character_plan_tick",
                run_at=now + timedelta(minutes=18),
                payload={"character_id": "char-002", "intent": "stay_on_task"},
                priority=2,
            ),
        ]
        for task in tasks:
            self.scheduler.schedule(task)
            self.scheduler_repository.save(task)

        event = WorldEvent(
            world_id=self.world_id,
            kind=WorldEventKind.WORLD_BOOTSTRAPPED,
            summary="World runtime bootstrapped with sample characters and tasks.",
            created_at=now,
            payload={"character_count": str(len(characters))},
        )
        self.event_bus.publish(event)
        self.event_repository.append(event)

    def advance(self, *, seconds: int = 15) -> list[WorldEvent]:
        self.clock.tick(seconds)
        due_tasks = self.scheduler.pop_due_tasks(clock=self.clock)
        published_events: list[WorldEvent] = []

        for task in due_tasks:
            self.scheduler_repository.remove(task.id)
            event = WorldEvent(
                world_id=self.world_id,
                kind=WorldEventKind.SCHEDULE_TRIGGERED,
                summary=(
                    f"Scheduled task {task.task_type} triggered for "
                    f"{task.payload.get('character_id', 'unknown')}."
                ),
                created_at=self.clock.snapshot().now,
                payload=task.payload,
            )
            self.event_bus.publish(event)
            self.event_repository.append(event)
            published_events.append(event)

        return published_events

    def get_world_state(self) -> WorldState:
        return WorldState(
            world_id=self.world_id,
            clock=self.clock.snapshot(),
            active_characters=self.character_repository.list_all(),
            recent_events=self.event_repository.recent_summaries(limit=10),
            pending_tasks=[
                f"{task.task_type}:{task.payload.get('character_id', 'unknown')}"
                for task in self.scheduler.snapshot()
            ],
        )
