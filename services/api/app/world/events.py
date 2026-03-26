from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class WorldEventKind(StrEnum):
    WORLD_BOOTSTRAPPED = "world_bootstrapped"
    SCHEDULE_TRIGGERED = "schedule_triggered"
    DIRECTOR_NOTE = "director_note"


class WorldEvent(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    world_id: str
    kind: WorldEventKind
    summary: str
    created_at: datetime
    payload: dict[str, str] = Field(default_factory=dict)


class RuntimeTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    world_id: str
    task_type: str
    run_at: datetime
    payload: dict[str, str] = Field(default_factory=dict)
    priority: int = 1

