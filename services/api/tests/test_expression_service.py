from app.agent_runtime.types import ActionType
from app.character.models import CharacterProfile
from app.expression.models import ExpressionInput, ExpressionRecentEvent
from app.expression.service import CharacterExpressionService
from app.expression.template import TemplateExpressionGenerator
from app.llm.expression_service import LLMExpressionService
from app.llm.interfaces import LLMClient


class FakeLLMClient(LLMClient):
    def __init__(self, payload: dict | None = None, *, should_fail: bool = False) -> None:
        self.payload = payload or {"content": "这是 LLM 生成的表达。"}
        self.should_fail = should_fail

    def generate(self, *, system_prompt: str, user_prompt: str) -> dict:
        if self.should_fail:
            raise RuntimeError("llm unavailable")
        assert system_prompt
        assert user_prompt
        return self.payload


def _build_expression_input(
    *,
    display_name: str,
    personality: str,
    speaking_style: str,
    social_drive: float,
    interrupt_threshold: float,
    emotion_state: str,
) -> ExpressionInput:
    return ExpressionInput(
        character_id=f"id-{display_name}",
        display_name=display_name,
        profile=CharacterProfile(
            identity_and_background=f"{display_name} 的身份背景。",
            personality=personality,
            speaking_style=speaking_style,
            appearance_and_presence=f"{display_name} 的外在气质。",
            additional_notes="",
        ),
        emotion_state=emotion_state,
        current_plan_summary="准备整理今天的群聊进展",
        social_drive=social_drive,
        interrupt_threshold=interrupt_threshold,
        action_type=ActionType.GROUP_MESSAGE,
        decision_reason="The character should check in with the group.",
        recent_context=[
            ExpressionRecentEvent(
                kind="director_note",
                summary="有人刚在世界里提到晚上的安排。",
            )
        ],
    )


def test_template_expression_generator_uses_character_state_to_produce_distinct_text() -> None:
    generator = TemplateExpressionGenerator()

    expressive = generator.generate(
        expression_input=_build_expression_input(
            display_name="林澈",
            personality="外向、主动、很会带气氛。",
            speaking_style="热络，喜欢主动接话。",
            social_drive=0.82,
            interrupt_threshold=0.45,
            emotion_state="curious",
        )
    )
    reserved = generator.generate(
        expression_input=_build_expression_input(
            display_name="许遥",
            personality="克制、谨慎、有边界感。",
            speaking_style="句子简短、直接，不爱铺垫。",
            social_drive=0.34,
            interrupt_threshold=0.72,
            emotion_state="focused",
        )
    )

    assert expressive.content != reserved.content
    assert "群里" in expressive.content
    assert "简短同步" in reserved.content


def test_expression_service_uses_llm_when_available() -> None:
    service = CharacterExpressionService(
        llm_expression_service=LLMExpressionService(FakeLLMClient()),
    )

    result = service.generate(
        expression_input=_build_expression_input(
            display_name="林澈",
            personality="外向。",
            speaking_style="热络。",
            social_drive=0.8,
            interrupt_threshold=0.4,
            emotion_state="curious",
        )
    )

    assert result.content == "这是 LLM 生成的表达。"
    assert result.generator_kind == "llm"
    assert result.used_fallback is False


def test_expression_service_falls_back_to_template_when_llm_fails() -> None:
    service = CharacterExpressionService(
        llm_expression_service=LLMExpressionService(FakeLLMClient(should_fail=True)),
    )

    result = service.generate(
        expression_input=_build_expression_input(
            display_name="许遥",
            personality="克制。",
            speaking_style="简短直接。",
            social_drive=0.3,
            interrupt_threshold=0.8,
            emotion_state="focused",
        )
    )

    assert result.generator_kind == "template"
    assert result.used_fallback is True
    assert "简短同步" in result.content
