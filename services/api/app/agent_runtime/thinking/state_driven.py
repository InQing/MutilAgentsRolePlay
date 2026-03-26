from app.agent_runtime.thinking.base import ThinkingEngine
from app.agent_runtime.types import (
    ActionDecision,
    ActionType,
    DirectorExplanation,
    VisibleContext,
)
from app.character.models import CharacterState


class StateDrivenThinkingEngine(ThinkingEngine):
    def decide(
        self,
        *,
        character_state: CharacterState,
        visible_context: VisibleContext,
    ) -> tuple[ActionDecision, DirectorExplanation]:
        if visible_context.task_intent == "check_group_chat":
            decision = ActionDecision(
                action_type=ActionType.GROUP_MESSAGE,
                reason="The current task is to check in with the main group conversation.",
                should_adjust_plan=False,
            )
            explanation = DirectorExplanation(
                summary=(
                    f"{character_state.display_name} reached a planned social check-in point "
                    "and decided to speak in the main group."
                ),
                confidence=0.88,
            )
            return decision, explanation

        direct_event = next(
            (
                event
                for event in visible_context.recent_events
                if event.is_directed_at_character
            ),
            None,
        )

        if direct_event and character_state.interrupt_threshold <= 0.7:
            decision = ActionDecision(
                action_type=ActionType.PRIVATE_MESSAGE,
                target_id=direct_event.source_character_id,
                reason="Respond to a directly relevant event while staying in character.",
                should_adjust_plan=False,
            )
            explanation = DirectorExplanation(
                summary=(
                    f"{character_state.display_name} detected a direct social prompt and "
                    "chose a private reply instead of ignoring it."
                ),
                confidence=0.86,
            )
            return decision, explanation

        if character_state.social_drive >= 0.75:
            decision = ActionDecision(
                action_type=ActionType.MOMENT_POST,
                reason="High social drive makes a public post feel natural right now.",
                should_adjust_plan=False,
            )
            explanation = DirectorExplanation(
                summary=(
                    f"{character_state.display_name} is socially active and likely to post "
                    "something visible to keep presence in the world."
                ),
                confidence=0.8,
            )
            return decision, explanation

        decision = ActionDecision(
            action_type=ActionType.IGNORE,
            reason="Stay with the current plan and conserve attention.",
            should_adjust_plan=False,
        )
        explanation = DirectorExplanation(
            summary=(
                f"{character_state.display_name} keeps the current rhythm because there is "
                "no high-priority trigger that justifies interrupting the plan."
            ),
            confidence=0.78,
        )
        return decision, explanation
