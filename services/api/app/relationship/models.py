from datetime import datetime

from pydantic import BaseModel, Field


class RelationshipSnapshot(BaseModel):
    source_character_id: str
    target_character_id: str
    affinity: float = Field(default=0.0, ge=-1.0, le=1.0)
    labels: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None
