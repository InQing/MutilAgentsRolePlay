from pydantic import BaseModel, Field

from app.agent_runtime.types import ActionType
from app.character.models import CharacterProfile


class ExpressionRecentEvent(BaseModel):
    kind: str
    summary: str
    source_character_id: str | None = None
    target_character_id: str | None = None
    is_directed_at_character: bool = False


class ExpressionInput(BaseModel):
    character_id: str
    display_name: str
    profile: CharacterProfile
    emotion_state: str
    current_plan_summary: str
    social_drive: float
    interrupt_threshold: float
    action_type: ActionType
    decision_reason: str
    target_id: str | None = None
    target_display_name: str | None = None
    recent_context: list[ExpressionRecentEvent] = Field(default_factory=list)


class ExpressionOutput(BaseModel):
    content: str
    generator_kind: str
    used_fallback: bool = False
