from pydantic import BaseModel, Field


class CharacterState(BaseModel):
    id: str
    display_name: str
    current_plan_summary: str
    emotion_state: str = "steady"
    social_drive: float = Field(default=0.5, ge=0.0, le=1.0)
    interrupt_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

