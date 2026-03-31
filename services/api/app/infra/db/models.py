from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class WorldRecord(Base):
    __tablename__ = "worlds"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    current_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    speed_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    paused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class CharacterRecord(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    profile: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    current_plan_summary: Mapped[str] = mapped_column(Text, nullable=False)
    emotion_state: Mapped[str] = mapped_column(String(64), nullable=False, default="steady")
    social_drive: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    interrupt_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)


class WorldEventRecord(Base):
    __tablename__ = "world_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class ScheduledTaskRecord(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    character_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    conversation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    conversation_meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class ChatMessageRecord(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversations.id"),
        nullable=False,
        index=True,
    )
    conversation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    mentions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)


class PlanRecord(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    character_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class MomentInteractionRecord(Base):
    __tablename__ = "moment_interactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    moment_message_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("chat_messages.id"),
        nullable=False,
        index=True,
    )
    interaction_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class RelationshipRecord(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "world_id",
            "source_character_id",
            "target_character_id",
            name="uq_relationships_world_source_target",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    world_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_character_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_character_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    affinity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    labels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
