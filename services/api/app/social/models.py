from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ConversationType(StrEnum):
    GROUP = "group"
    PRIVATE = "private"
    MOMENT = "moment"


class MessageRecord(BaseModel):
    id: str
    conversation_id: str
    conversation_type: ConversationType
    sender_id: str
    content: str
    created_at: datetime
    target_id: str | None = None
    mentions: list[str] = Field(default_factory=list)

