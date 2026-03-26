from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.agent_runtime.types import ActionType, VisibleContext, VisibleEvent
from app.character.models import CharacterState


def test_state_driven_engine_prefers_private_reply_for_direct_event() -> None:
    engine = StateDrivenThinkingEngine()
    character = CharacterState(
        id="char-001",
        display_name="林澈",
        current_plan_summary="在咖啡馆整理消息",
        social_drive=0.4,
        interrupt_threshold=0.4,
    )
    context = VisibleContext(
        character_id="char-001",
        current_plan_summary=character.current_plan_summary,
        recent_events=[
            VisibleEvent(
                kind="message",
                summary="许遥单独来问一个问题",
                source_character_id="char-002",
                target_character_id="char-001",
                is_directed_at_character=True,
            )
        ],
    )

    decision, explanation = engine.decide(
        character_state=character,
        visible_context=context,
    )

    assert decision.action_type == ActionType.PRIVATE_MESSAGE
    assert decision.target_id == "char-002"
    assert explanation.confidence > 0.8

