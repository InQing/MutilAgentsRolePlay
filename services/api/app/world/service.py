from datetime import datetime, timedelta, timezone

from app.agent_runtime.thinking.base import ThinkingEngine
from app.agent_runtime.types import ActionDecision, ActionType, VisibleContext, VisibleEvent
from app.character.models import CharacterState, build_default_character_profile
from app.infra.db.repositories import (
    CharacterRepository,
    PlanRepository,
    SchedulerRepository,
    WorldEventRepository,
)
from app.plan.models import PlanItem
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
        self.plan_repository = PlanRepository()
        self.event_repository = WorldEventRepository()
        self.scheduler_repository = SchedulerRepository()
        self.world_id = "local-prototype"
        self._next_event_sequence = 1

    def bootstrap_sample_world(self) -> None:
        if self.character_repository.list_all():
            return

        characters = [
            CharacterState(
                id="char-001",
                display_name="林澈",
                profile=build_default_character_profile(
                    character_id="char-001",
                    display_name="林澈",
                ),
                current_plan_summary="整理今天的群聊动态并准备晚上的聚会",
                emotion_state="curious",
                social_drive=0.82,
                interrupt_threshold=0.45,
            ),
            CharacterState(
                id="char-002",
                display_name="许遥",
                profile=build_default_character_profile(
                    character_id="char-002",
                    display_name="许遥",
                ),
                current_plan_summary="专注完成工作，在必要时才回复消息",
                emotion_state="focused",
                social_drive=0.34,
                interrupt_threshold=0.72,
            ),
        ]
        self.character_repository.save_many(characters)

        now = datetime.now(timezone.utc)
        plans = [
            PlanItem(
                character_id="char-001",
                summary=characters[0].current_plan_summary,
                intent="check_group_chat",
                next_run_at=now + timedelta(minutes=10),
                priority=1,
            ),
            PlanItem(
                character_id="char-002",
                summary=characters[1].current_plan_summary,
                intent="stay_on_task",
                next_run_at=now + timedelta(minutes=18),
                priority=2,
            ),
        ]
        for plan in plans:
            self.plan_repository.save(plan)
            task = self._build_task_from_plan(plan)
            self.scheduler.schedule(task)
            self.scheduler_repository.save(task)

        event = WorldEvent(
            world_id=self.world_id,
            kind=WorldEventKind.WORLD_BOOTSTRAPPED,
            summary="World runtime bootstrapped with sample characters and tasks.",
            created_at=now,
            payload={"character_count": str(len(characters))},
        )
        self.record_event(event)

    def advance(self, *, seconds: int = 15) -> tuple[list[RuntimeTask], list[WorldEvent]]:
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
            self.record_event(event)
            published_events.append(event)

        return due_tasks, published_events

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

    def get_recent_events(self, *, limit: int = 10) -> list[WorldEvent]:
        return self.event_repository.list_all()[-limit:]

    def list_characters(self) -> list[CharacterState]:
        return self.character_repository.list_all()

    def list_plans(self) -> list[PlanItem]:
        return self.plan_repository.list_all()

    def get_pending_tasks(self) -> list[RuntimeTask]:
        return self.scheduler.snapshot()

    def get_character(self, character_id: str | None) -> CharacterState | None:
        return self.character_repository.get(character_id)

    def pick_peer_character_id(self, *, exclude_id: str) -> str | None:
        for character in self.character_repository.list_all():
            if character.id != exclude_id:
                return character.id
        return None

    def get_plan(self, plan_id: str | None) -> PlanItem | None:
        return self.plan_repository.get(plan_id)

    def build_visible_context(
        self,
        *,
        character: CharacterState,
        task: RuntimeTask,
    ) -> VisibleContext:
        recent_visible_events = [
            VisibleEvent(
                kind=event.kind.value,
                summary=event.summary,
                source_character_id=event.payload.get("character_id"),
                target_character_id=event.payload.get("target_character_id"),
                is_directed_at_character=event.payload.get("target_character_id") == character.id,
            )
            for event in self.get_recent_events(limit=5)
        ]
        return VisibleContext(
            character_id=character.id,
            current_plan_summary=character.current_plan_summary,
            task_intent=task.payload.get("intent") or self._resolve_task_intent(task),
            recent_events=recent_visible_events,
        )

    def record_event(self, event: WorldEvent) -> None:
        if event.sequence_number <= 0:
            event.sequence_number = self._next_event_sequence
            self._next_event_sequence += 1
        else:
            self._next_event_sequence = max(self._next_event_sequence, event.sequence_number + 1)
        self.event_bus.publish(event)
        self.event_repository.append(event)

    def add_character(self, *, character: CharacterState) -> RuntimeTask:
        self.character_repository.save(character)
        plan = self._build_initial_plan_for_character(character=character)
        self.plan_repository.save(plan)
        task = self._build_task_from_plan(plan)
        self.scheduler.schedule(task)
        self.scheduler_repository.save(task)
        return task

    def update_character(self, *, character: CharacterState) -> CharacterState:
        self.character_repository.save(character)
        existing_plan = self.plan_repository.get_active_for_character(character_id=character.id)
        if existing_plan is not None:
            self.plan_repository.save(
                existing_plan.model_copy(
                    update={
                        "summary": character.current_plan_summary,
                        "updated_at": self.clock.snapshot().now,
                    }
                )
            )
        return character

    def remove_character(self, *, character_id: str) -> CharacterState | None:
        character = self.character_repository.remove(character_id)
        if character is None:
            return None

        removed_plans = self.plan_repository.remove_for_character(character_id=character_id)
        for plan in removed_plans:
            removed_tasks = self.scheduler.remove_for_plan(plan_id=plan.id)
            for task in removed_tasks:
                self.scheduler_repository.remove(task.id)

        dangling_tasks = self.scheduler.remove_for_character(character_id=character_id)
        for task in dangling_tasks:
            self.scheduler_repository.remove(task.id)
        return character

    def schedule_follow_up_task(
        self,
        *,
        character: CharacterState,
        previous_decision: ActionDecision,
    ) -> RuntimeTask:
        if previous_decision.action_type == ActionType.GROUP_MESSAGE:
            intent = "share_update"
            delay_minutes = 12
        elif previous_decision.action_type == ActionType.MOMENT_POST:
            intent = "check_group_chat"
            delay_minutes = 14
        elif previous_decision.action_type == ActionType.PRIVATE_MESSAGE:
            intent = "stay_on_task"
            delay_minutes = 16
        else:
            intent = "check_group_chat" if character.social_drive >= 0.6 else "stay_on_task"
            delay_minutes = 18

        next_run_at = self.clock.snapshot().now + timedelta(minutes=delay_minutes)
        existing_plan = self.plan_repository.get_active_for_character(character_id=character.id)
        if existing_plan is None:
            plan = PlanItem(
                character_id=character.id,
                summary=character.current_plan_summary,
                intent=intent,
                next_run_at=next_run_at,
                priority=1,
            )
        else:
            plan = existing_plan.model_copy(
                update={
                    "summary": character.current_plan_summary,
                    "intent": intent,
                    "next_run_at": next_run_at,
                    "priority": 1,
                    "updated_at": self.clock.snapshot().now,
                }
            )
            removed_tasks = self.scheduler.remove_for_plan(plan_id=plan.id)
            for task in removed_tasks:
                self.scheduler_repository.remove(task.id)

        self.plan_repository.save(plan)
        next_task = self._build_task_from_plan(plan)
        self.scheduler.schedule(next_task)
        self.scheduler_repository.save(next_task)
        return next_task

    def replace_runtime_state(
        self,
        *,
        clock_state,
        characters: list[CharacterState],
        plans: list[PlanItem],
        tasks: list[RuntimeTask],
        events: list[WorldEvent],
    ) -> None:
        self.clock.load_snapshot(clock_state)
        self.character_repository.replace_all(characters)
        self.plan_repository.replace_all(plans)
        self.scheduler.replace(tasks)
        self.scheduler_repository.replace_all(tasks)
        self.event_bus.replace_history(events)
        self.event_repository.replace_all(events)
        self._next_event_sequence = (
            max((event.sequence_number for event in events), default=0) + 1
        )

    def _build_task_from_plan(self, plan: PlanItem) -> RuntimeTask:
        return RuntimeTask(
            world_id=self.world_id,
            task_type="character_plan_tick",
            run_at=plan.next_run_at,
            payload={
                "character_id": plan.character_id,
                "intent": plan.intent,
                "plan_id": plan.id,
            },
            priority=plan.priority,
        )

    def _build_initial_plan_for_character(self, *, character: CharacterState) -> PlanItem:
        initial_intent = "check_group_chat" if character.social_drive >= 0.6 else "stay_on_task"
        initial_delay_minutes = 10 if character.social_drive >= 0.6 else 18
        return PlanItem(
            character_id=character.id,
            summary=character.current_plan_summary,
            intent=initial_intent,
            next_run_at=self.clock.snapshot().now + timedelta(minutes=initial_delay_minutes),
            priority=1,
        )

    def _resolve_task_intent(self, task: RuntimeTask) -> str | None:
        plan = self.get_plan(task.payload.get("plan_id"))
        if plan is None:
            return None
        return plan.intent
