from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class VisibilityMode(StrEnum):
    REALTIME = "realtime"
    DELAYED = "delayed"
    HIDDEN = "hidden"


class PermissionView(BaseModel):
    private_chat_visibility: VisibilityMode
    plan_visibility: VisibilityMode
    relationship_visibility: VisibilityMode
    can_inject_events: bool
    can_control_world: bool


class UpdateWorldSpeedRequest(BaseModel):
    speed_multiplier: float = Field(gt=0.0)


class InjectDirectorEventRequest(BaseModel):
    summary: str
    target_character_id: str | None = None
    task_intent: str | None = None

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("summary must not be empty")
        return normalized

    @field_validator("target_character_id", "task_intent")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class DirectorLogEntry(BaseModel):
    event_id: str
    sequence_number: int
    kind: str
    summary: str
    created_at: datetime
    character_id: str | None = None
    director_explanation: str | None = None


class DirectorConversationPreview(BaseModel):
    id: str
    title: str
    conversation_type: str
    participant_ids: list[str] = Field(default_factory=list)
    last_message_preview: str | None = None
    last_message_sender_id: str | None = None
    last_message_sender_name: str | None = None
    last_message_at: datetime | None = None


class DirectorCharacterSnapshot(BaseModel):
    id: str
    display_name: str
    emotion_state: str
    current_plan_summary: str
    social_drive: float
    interrupt_threshold: float
    next_task_type: str | None = None
    next_task_intent: str | None = None
    next_task_run_at: datetime | None = None


class DirectorRelationshipEdge(BaseModel):
    source_character_id: str
    source_display_name: str
    target_character_id: str
    target_display_name: str
    affinity: float
    labels: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None


class DirectorMomentInteractionEntry(BaseModel):
    id: str
    interaction_type: str
    actor_id: str
    actor_display_name: str
    target_moment_id: str
    target_moment_preview: str
    target_moment_sender_id: str | None = None
    target_moment_sender_name: str | None = None
    content: str | None = None
    created_at: datetime


class DirectorPanelState(BaseModel):
    world_id: str
    current_time: datetime
    speed_multiplier: float
    paused: bool
    director_visibility_delay_seconds: int
    pending_task_count: int
    permissions: PermissionView
    characters: list[DirectorCharacterSnapshot] = Field(default_factory=list)
    relationships: list[DirectorRelationshipEdge] = Field(default_factory=list)
    conversations: list[DirectorConversationPreview] = Field(default_factory=list)
    moment_interactions: list[DirectorMomentInteractionEntry] = Field(default_factory=list)
    recent_logs: list[DirectorLogEntry] = Field(default_factory=list)
