from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class CharacterRecord(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    current_plan_summary: Mapped[str] = mapped_column(Text, nullable=False)
    emotion_state: Mapped[str] = mapped_column(String(64), nullable=False, default="steady")
    social_drive: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    interrupt_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)


class WorldEventRecord(Base):
    __tablename__ = "world_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
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

