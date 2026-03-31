from app.agent_runtime.types import ActionDecision, ActionType
from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.world.service import WorldRuntimeService


def test_follow_up_tasks_are_derived_from_persisted_plans() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()

    character = runtime.get_character("char-001")
    assert character is not None

    original_plan = runtime.list_plans()[0]
    runtime.schedule_follow_up_task(
        character=character,
        previous_decision=ActionDecision(
            action_type=ActionType.MOMENT_POST,
            reason="Keep the world moving after the moment post.",
        ),
    )

    updated_plan = runtime.get_plan(original_plan.id)
    assert updated_plan is not None
    assert updated_plan.intent == "check_group_chat"

    pending_task = next(
        task for task in runtime.get_pending_tasks()
        if task.payload.get("plan_id") == original_plan.id
    )
    assert pending_task.payload["intent"] == updated_plan.intent
    assert pending_task.run_at == updated_plan.next_run_at
