from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.world.events import RuntimeTask
from app.world.service import WorldRuntimeService


def test_world_runtime_bootstrap_contains_characters_and_tasks() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )

    runtime.bootstrap_sample_world()
    state = runtime.get_world_state()
    pending_tasks = runtime.get_pending_tasks()
    plans = runtime.list_plans()

    assert len(state.active_characters) == 2
    assert len(state.pending_tasks) == 2
    assert len(plans) == 2
    assert all(task.payload.get("plan_id") for task in pending_tasks)
    assert "World runtime bootstrapped" in state.recent_events[-1]


def test_world_runtime_advance_consumes_due_tasks() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()

    first_task = runtime.scheduler.snapshot()[0]
    runtime.scheduler.schedule(
        RuntimeTask(
            world_id=runtime.world_id,
            task_type="manual_test",
            run_at=runtime.clock.snapshot().now,
            payload={"character_id": "char-001"},
            priority=1,
        )
    )

    _, events = runtime.advance(seconds=1)

    assert events
    assert any(event.payload.get("character_id") == "char-001" for event in events)
    assert any("char-001" in summary for summary in runtime.get_world_state().recent_events)
    assert first_task.id in {task.id for task in runtime.scheduler.snapshot()}


def test_world_runtime_can_replace_persisted_state() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()
    original_events = runtime.get_recent_events(limit=10)

    runtime.replace_runtime_state(
        clock_state=runtime.clock.snapshot(),
        characters=runtime.character_repository.list_all()[:1],
        plans=runtime.list_plans()[:1],
        tasks=[],
        events=original_events[:1],
    )

    state = runtime.get_world_state()

    assert len(state.active_characters) == 1
    assert state.pending_tasks == []
    assert len(state.recent_events) == 1
