from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class PlanStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"


class PlanItem(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    character_id: str
    summary: str
    intent: str
    next_run_at: datetime
    priority: int = 1
    status: PlanStatus = PlanStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
