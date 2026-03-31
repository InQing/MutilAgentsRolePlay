from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class WorldEventKind(str, Enum):
    WORLD_BOOTSTRAPPED = "world_bootstrapped"
    SCHEDULE_TRIGGERED = "schedule_triggered"
    DIRECTOR_NOTE = "director_note"
    ACTION_EXECUTED = "action_executed"
    ACTION_SKIPPED = "action_skipped"
    MOMENT_INTERACTION_RECORDED = "moment_interaction_recorded"
    RELATIONSHIP_UPDATED = "relationship_updated"
    CHARACTER_CREATED = "character_created"
    CHARACTER_UPDATED = "character_updated"
    CHARACTER_DELETED = "character_deleted"


class WorldEvent(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    sequence_number: int = 0
    world_id: str
    kind: WorldEventKind
    summary: str
    created_at: datetime
    payload: dict[str, str] = Field(default_factory=dict)

    @property
    def summary_text(self) -> str:
        return self.summary


class RuntimeTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    world_id: str
    task_type: str
    run_at: datetime
    payload: dict[str, str] = Field(default_factory=dict)
    priority: int = 1
