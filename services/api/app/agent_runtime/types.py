from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    GROUP_MESSAGE = "group_message"
    PRIVATE_MESSAGE = "private_message"
    MOMENT_POST = "moment_post"
    MOMENT_COMMENT = "moment_comment"
    PLAN_UPDATE = "plan_update"
    IGNORE = "ignore"


class VisibleEvent(BaseModel):
    kind: str
    summary: str
    source_character_id: str | None = None
    target_character_id: str | None = None
    is_directed_at_character: bool = False


class VisibleContext(BaseModel):
    character_id: str
    current_plan_summary: str
    task_intent: str | None = None
    recent_events: list[VisibleEvent] = Field(default_factory=list)


class ActionDecision(BaseModel):
    action_type: ActionType
    target_id: str | None = None
    reason: str
    should_adjust_plan: bool = False


class DirectorExplanation(BaseModel):
    summary: str
    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
