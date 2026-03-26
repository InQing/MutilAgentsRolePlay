from datetime import datetime

from pydantic import BaseModel, Field

from app.character.models import CharacterState


class ClockState(BaseModel):
    now: datetime
    speed_multiplier: float = 1.0
    paused: bool = False


class WorldState(BaseModel):
    world_id: str
    clock: ClockState
    active_characters: list[CharacterState] = Field(default_factory=list)
    recent_events: list[str] = Field(default_factory=list)
    pending_tasks: list[str] = Field(default_factory=list)
