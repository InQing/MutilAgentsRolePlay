from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ConversationType(str, Enum):
    GROUP = "group"
    PRIVATE = "private"
    MOMENT = "moment"


class MessageRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    conversation_id: str
    conversation_type: ConversationType
    sender_id: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    target_id: str | None = None
    mentions: list[str] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    id: str
    title: str
    conversation_type: ConversationType
    participant_ids: list[str] = Field(default_factory=list)


class CreateMessageRequest(BaseModel):
    conversation_id: str
    conversation_type: ConversationType
    sender_id: str
    content: str
    target_id: str | None = None
    mentions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content must not be empty")
        return normalized


class CreatePrivateMessageRequest(BaseModel):
    sender_id: str
    target_id: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content must not be empty")
        return normalized


class CreateMomentRequest(BaseModel):
    sender_id: str
    content: str
    mentions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content must not be empty")
        return normalized
