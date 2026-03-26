from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.character.models import CharacterState
from app.infra.db.models import (
    CharacterRecord,
    ChatMessageRecord,
    ConversationRecord,
    RelationshipRecord,
    ScheduledTaskRecord,
    WorldEventRecord,
    WorldRecord,
)
from app.relationship.models import RelationshipSnapshot
from app.social.models import ConversationSummary, ConversationType, CreateMessageRequest, MessageRecord
from app.world.models import ClockState
from app.world.events import RuntimeTask, WorldEvent


class CharacterRepository:
    def __init__(self) -> None:
        self._characters: dict[str, CharacterState] = {}

    def save_many(self, characters: Sequence[CharacterState]) -> None:
        for character in characters:
            self._characters[character.id] = character

    def list_all(self) -> list[CharacterState]:
        return list(self._characters.values())

    def replace_all(self, characters: Sequence[CharacterState]) -> None:
        self._characters = {character.id: character for character in characters}


class WorldEventRepository:
    def __init__(self) -> None:
        self._events: list[WorldEvent] = []

    def append(self, event: WorldEvent) -> None:
        self._events.append(event)

    def recent_summaries(self, *, limit: int = 10) -> list[str]:
        return [event.summary for event in self._events[-limit:]]

    def list_all(self) -> list[WorldEvent]:
        return list(self._events)

    def replace_all(self, events: Sequence[WorldEvent]) -> None:
        self._events = list(events)


class SchedulerRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, RuntimeTask] = {}

    def save(self, task: RuntimeTask) -> None:
        self._tasks[task.id] = task

    def remove(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)

    def list_all(self) -> list[RuntimeTask]:
        return list(self._tasks.values())

    def replace_all(self, tasks: Sequence[RuntimeTask]) -> None:
        self._tasks = {task.id: task for task in tasks}


class AsyncWorldRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, world_id: str) -> ClockState | None:
        record = await self.session.get(WorldRecord, world_id)
        if record is None:
            return None
        return ClockState(
            now=record.current_time,
            speed_multiplier=record.speed_multiplier,
            paused=record.paused,
        )

    async def upsert(self, *, world_id: str, clock: ClockState) -> None:
        record = await self.session.get(WorldRecord, world_id)
        if record is None:
            record = WorldRecord(
                id=world_id,
                current_time=clock.now,
                speed_multiplier=clock.speed_multiplier,
                paused=clock.paused,
            )
            self.session.add(record)
            return

        record.current_time = clock.now
        record.speed_multiplier = clock.speed_multiplier
        record.paused = clock.paused


class AsyncCharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replace_for_world(
        self,
        *,
        world_id: str,
        characters: Sequence[CharacterState],
    ) -> None:
        await self.session.execute(
            delete(CharacterRecord).where(CharacterRecord.world_id == world_id)
        )
        self.session.add_all(
            [
                CharacterRecord(
                    id=character.id,
                    world_id=world_id,
                    display_name=character.display_name,
                    current_plan_summary=character.current_plan_summary,
                    emotion_state=character.emotion_state,
                    social_drive=character.social_drive,
                    interrupt_threshold=character.interrupt_threshold,
                )
                for character in characters
            ]
        )

    async def list_for_world(self, *, world_id: str) -> list[CharacterState]:
        result = await self.session.execute(
            select(CharacterRecord).where(CharacterRecord.world_id == world_id)
        )
        return [
            CharacterState(
                id=record.id,
                display_name=record.display_name,
                current_plan_summary=record.current_plan_summary,
                emotion_state=record.emotion_state,
                social_drive=record.social_drive,
                interrupt_threshold=record.interrupt_threshold,
            )
            for record in result.scalars().all()
        ]


class AsyncWorldEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append_many(self, events: Sequence[WorldEvent]) -> None:
        existing_ids = {
            record_id
            for record_id in (
                await self.session.execute(
                    select(WorldEventRecord.id).where(
                        WorldEventRecord.id.in_([event.id for event in events])
                    )
                )
            ).scalars()
        }
        self.session.add_all(
            [
                WorldEventRecord(
                    id=event.id,
                    sequence_number=event.sequence_number,
                    world_id=event.world_id,
                    kind=event.kind.value,
                    summary=event.summary,
                    created_at=event.created_at,
                    payload=event.payload,
                )
                for event in events
                if event.id not in existing_ids
            ]
        )

    async def list_recent_for_world(
        self,
        *,
        world_id: str,
        limit: int = 10,
    ) -> list[WorldEvent]:
        result = await self.session.execute(
            select(WorldEventRecord)
            .where(WorldEventRecord.world_id == world_id)
            .order_by(WorldEventRecord.sequence_number.desc())
            .limit(limit)
        )
        records = list(result.scalars().all())
        records.reverse()
        return [
            WorldEvent(
                id=record.id,
                sequence_number=record.sequence_number,
                world_id=record.world_id,
                kind=record.kind,
                summary=record.summary,
                created_at=record.created_at,
                payload=record.payload,
            )
            for record in records
        ]


class AsyncSchedulerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replace_for_world(self, *, world_id: str, tasks: Sequence[RuntimeTask]) -> None:
        await self.session.execute(
            delete(ScheduledTaskRecord).where(ScheduledTaskRecord.world_id == world_id)
        )
        self.session.add_all(
            [
                ScheduledTaskRecord(
                    id=task.id,
                    world_id=task.world_id,
                    task_type=task.task_type,
                    character_id=task.payload.get("character_id"),
                    run_at=task.run_at,
                    payload=task.payload,
                    priority=task.priority,
                )
                for task in tasks
            ]
        )

    async def list_for_world(self, *, world_id: str) -> list[RuntimeTask]:
        result = await self.session.execute(
            select(ScheduledTaskRecord)
            .where(ScheduledTaskRecord.world_id == world_id)
            .order_by(ScheduledTaskRecord.run_at.asc(), ScheduledTaskRecord.priority.asc())
        )
        return [
            RuntimeTask(
                id=record.id,
                world_id=record.world_id,
                task_type=record.task_type,
                run_at=record.run_at,
                payload=record.payload,
                priority=record.priority,
            )
            for record in result.scalars().all()
        ]


class AsyncConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_defaults(self, *, world_id: str) -> None:
        result = await self.session.execute(
            select(ConversationRecord.id).where(ConversationRecord.world_id == world_id)
        )
        existing_ids = set(result.scalars().all())
        defaults = [
            ConversationRecord(
                id="conv-general",
                world_id=world_id,
                title="世界群聊",
                conversation_type=ConversationType.GROUP.value,
                conversation_meta={"participant_ids": []},
            ),
            ConversationRecord(
                id="conv-moments",
                world_id=world_id,
                title="朋友圈",
                conversation_type=ConversationType.MOMENT.value,
                conversation_meta={"participant_ids": []},
            ),
        ]
        self.session.add_all(
            [record for record in defaults if record.id not in existing_ids]
        )

    async def list_for_world(self, *, world_id: str) -> list[ConversationSummary]:
        result = await self.session.execute(
            select(ConversationRecord)
            .where(ConversationRecord.world_id == world_id)
            .order_by(ConversationRecord.title.asc())
        )
        return [
            ConversationSummary(
                id=record.id,
                title=record.title,
                conversation_type=record.conversation_type,
                participant_ids=record.conversation_meta.get("participant_ids", []),
            )
            for record in result.scalars().all()
        ]

    async def ensure_private_conversation(
        self,
        *,
        world_id: str,
        participant_ids: list[str],
    ) -> ConversationSummary:
        normalized = sorted(participant_ids)
        result = await self.session.execute(
            select(ConversationRecord).where(
                ConversationRecord.world_id == world_id,
                ConversationRecord.conversation_type == ConversationType.PRIVATE.value,
            )
        )
        for record in result.scalars().all():
            if sorted(record.conversation_meta.get("participant_ids", [])) == normalized:
                return ConversationSummary(
                    id=record.id,
                    title=record.title,
                    conversation_type=record.conversation_type,
                    participant_ids=record.conversation_meta.get("participant_ids", []),
                )

        title = " / ".join(normalized)
        record = ConversationRecord(
            id=f"conv-private-{uuid4().hex}",
            world_id=world_id,
            title=title,
            conversation_type=ConversationType.PRIVATE.value,
            conversation_meta={"participant_ids": normalized},
        )
        self.session.add(record)
        await self.session.flush()
        return ConversationSummary(
            id=record.id,
            title=record.title,
            conversation_type=record.conversation_type,
            participant_ids=normalized,
        )


class AsyncMessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_conversation(self, *, conversation_id: str) -> list[MessageRecord]:
        result = await self.session.execute(
            select(ChatMessageRecord)
            .where(ChatMessageRecord.conversation_id == conversation_id)
            .order_by(ChatMessageRecord.created_at.asc())
        )
        return [
            MessageRecord(
                id=record.id,
                conversation_id=record.conversation_id,
                conversation_type=record.conversation_type,
                sender_id=record.sender_id,
                content=record.content,
                created_at=record.created_at,
                target_id=record.target_id,
                mentions=record.mentions,
            )
            for record in result.scalars().all()
        ]

    async def create_for_world(
        self,
        *,
        world_id: str,
        request: CreateMessageRequest,
    ) -> MessageRecord:
        message = MessageRecord(
            conversation_id=request.conversation_id,
            conversation_type=request.conversation_type,
            sender_id=request.sender_id,
            content=request.content,
            created_at=request.created_at,
            target_id=request.target_id,
            mentions=request.mentions,
        )
        record = ChatMessageRecord(
            id=message.id,
            world_id=world_id,
            conversation_id=message.conversation_id,
            conversation_type=message.conversation_type,
            sender_id=message.sender_id,
            content=message.content,
            created_at=message.created_at,
            target_id=message.target_id,
            mentions=message.mentions,
        )
        self.session.add(record)
        return message


class AsyncRelationshipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_defaults_for_world(
        self,
        *,
        world_id: str,
        character_ids: Sequence[str],
    ) -> None:
        normalized_ids = sorted(set(character_ids))
        expected_pairs = [
            (source_id, target_id)
            for source_id in normalized_ids
            for target_id in normalized_ids
            if source_id != target_id
        ]
        if not expected_pairs:
            return

        result = await self.session.execute(
            select(
                RelationshipRecord.source_character_id,
                RelationshipRecord.target_character_id,
            ).where(RelationshipRecord.world_id == world_id)
        )
        existing_pairs = set(result.all())
        current_time = datetime.now(timezone.utc)

        self.session.add_all(
            [
                RelationshipRecord(
                    id=f"rel-{uuid4().hex}",
                    world_id=world_id,
                    source_character_id=source_id,
                    target_character_id=target_id,
                    affinity=0.0,
                    labels=[],
                    updated_at=current_time,
                )
                for source_id, target_id in expected_pairs
                if (source_id, target_id) not in existing_pairs
            ]
        )

    async def list_for_world(self, *, world_id: str) -> list[RelationshipSnapshot]:
        result = await self.session.execute(
            select(RelationshipRecord)
            .where(RelationshipRecord.world_id == world_id)
            .order_by(RelationshipRecord.affinity.desc(), RelationshipRecord.updated_at.desc())
        )
        return [
            RelationshipSnapshot(
                source_character_id=record.source_character_id,
                target_character_id=record.target_character_id,
                affinity=record.affinity,
                labels=record.labels,
                updated_at=record.updated_at,
            )
            for record in result.scalars().all()
        ]

    async def apply_affinity_delta(
        self,
        *,
        world_id: str,
        source_character_id: str,
        target_character_id: str,
        delta: float,
        label: str,
        updated_at: datetime,
    ) -> RelationshipSnapshot:
        result = await self.session.execute(
            select(RelationshipRecord).where(
                RelationshipRecord.world_id == world_id,
                RelationshipRecord.source_character_id == source_character_id,
                RelationshipRecord.target_character_id == target_character_id,
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            record = RelationshipRecord(
                id=f"rel-{uuid4().hex}",
                world_id=world_id,
                source_character_id=source_character_id,
                target_character_id=target_character_id,
                affinity=0.0,
                labels=[],
                updated_at=updated_at,
            )
            self.session.add(record)

        record.affinity = max(-1.0, min(1.0, record.affinity + delta))
        record.updated_at = updated_at
        if label and label not in record.labels:
            record.labels = [*record.labels[-2:], label]

        return RelationshipSnapshot(
            source_character_id=record.source_character_id,
            target_character_id=record.target_character_id,
            affinity=record.affinity,
            labels=record.labels,
            updated_at=record.updated_at,
        )
