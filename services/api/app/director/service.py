import asyncio

from app.character.models import CharacterState
from app.director.models import (
    DirectorCharacterSnapshot,
    DirectorConversationPreview,
    DirectorLogEntry,
    DirectorPanelState,
    DirectorRelationshipEdge,
)
from app.relationship.models import RelationshipSnapshot
from app.relationship.service import RelationshipService
from app.social.models import ConversationSummary, MessageRecord
from app.social.service import SocialService
from app.world.events import RuntimeTask
from app.world.service import WorldRuntimeService


class DirectorPanelService:
    def __init__(
        self,
        *,
        world_runtime: WorldRuntimeService,
        social_service: SocialService,
        relationship_service: RelationshipService,
        permission_policy,
        director_visibility_delay_seconds: int,
    ) -> None:
        self.world_runtime = world_runtime
        self.social_service = social_service
        self.relationship_service = relationship_service
        self.permission_policy = permission_policy
        self.director_visibility_delay_seconds = director_visibility_delay_seconds

    async def get_panel_state(self) -> DirectorPanelState:
        permissions = self.permission_policy.describe_view()
        clock = self.world_runtime.clock.snapshot()
        characters = self.world_runtime.list_characters()
        pending_tasks = self.world_runtime.get_pending_tasks()
        character_lookup = {character.id: character for character in characters}

        return DirectorPanelState(
            world_id=self.world_runtime.world_id,
            current_time=clock.now,
            speed_multiplier=clock.speed_multiplier,
            paused=clock.paused,
            director_visibility_delay_seconds=self.director_visibility_delay_seconds,
            pending_task_count=len(pending_tasks),
            permissions=permissions,
            characters=self._build_character_snapshots(characters, pending_tasks),
            relationships=await self._build_relationship_edges(character_lookup),
            conversations=await self._build_conversation_previews(character_lookup),
            recent_logs=self._build_recent_logs(),
        )

    def _build_character_snapshots(
        self,
        characters: list[CharacterState],
        pending_tasks: list[RuntimeTask],
    ) -> list[DirectorCharacterSnapshot]:
        next_task_by_character: dict[str, RuntimeTask] = {}
        for task in sorted(
            pending_tasks,
            key=lambda item: (item.run_at, item.priority, item.id),
        ):
            character_id = task.payload.get("character_id")
            if character_id is None or character_id in next_task_by_character:
                continue
            next_task_by_character[character_id] = task

        snapshots: list[DirectorCharacterSnapshot] = []
        for character in characters:
            next_task = next_task_by_character.get(character.id)
            snapshots.append(
                DirectorCharacterSnapshot(
                    id=character.id,
                    display_name=character.display_name,
                    emotion_state=character.emotion_state,
                    current_plan_summary=character.current_plan_summary,
                    social_drive=character.social_drive,
                    interrupt_threshold=character.interrupt_threshold,
                    next_task_type=next_task.task_type if next_task is not None else None,
                    next_task_intent=next_task.payload.get("intent") if next_task is not None else None,
                    next_task_run_at=next_task.run_at if next_task is not None else None,
                )
            )
        return snapshots

    async def _build_conversation_previews(
        self,
        character_lookup: dict[str, CharacterState],
    ) -> list[DirectorConversationPreview]:
        conversations = await self.social_service.list_conversations()
        message_results = await asyncio.gather(
            *[
                self.social_service.list_messages(conversation_id=conversation.id)
                for conversation in conversations
            ]
        )

        previews: list[DirectorConversationPreview] = []
        for conversation, messages in zip(conversations, message_results, strict=False):
            previews.append(
                self._build_conversation_preview(
                    conversation=conversation,
                    messages=messages,
                    character_lookup=character_lookup,
                )
            )
        return previews

    async def _build_relationship_edges(
        self,
        character_lookup: dict[str, CharacterState],
    ) -> list[DirectorRelationshipEdge]:
        relationships = await self.relationship_service.list_relationships()
        return [
            self._build_relationship_edge(
                relationship=relationship,
                character_lookup=character_lookup,
            )
            for relationship in relationships
        ]

    def _build_conversation_preview(
        self,
        *,
        conversation: ConversationSummary,
        messages: list[MessageRecord],
        character_lookup: dict[str, CharacterState],
    ) -> DirectorConversationPreview:
        latest_message = messages[-1] if messages else None
        sender = (
            character_lookup.get(latest_message.sender_id)
            if latest_message is not None
            else None
        )
        return DirectorConversationPreview(
            id=conversation.id,
            title=conversation.title,
            conversation_type=conversation.conversation_type.value,
            participant_ids=conversation.participant_ids,
            last_message_preview=self._truncate_message(latest_message.content)
            if latest_message is not None
            else None,
            last_message_sender_id=latest_message.sender_id if latest_message is not None else None,
            last_message_sender_name=sender.display_name if sender is not None else None,
            last_message_at=latest_message.created_at if latest_message is not None else None,
        )

    def _build_relationship_edge(
        self,
        *,
        relationship: RelationshipSnapshot,
        character_lookup: dict[str, CharacterState],
    ) -> DirectorRelationshipEdge:
        source_character = character_lookup.get(relationship.source_character_id)
        target_character = character_lookup.get(relationship.target_character_id)
        return DirectorRelationshipEdge(
            source_character_id=relationship.source_character_id,
            source_display_name=source_character.display_name
            if source_character is not None
            else relationship.source_character_id,
            target_character_id=relationship.target_character_id,
            target_display_name=target_character.display_name
            if target_character is not None
            else relationship.target_character_id,
            affinity=relationship.affinity,
            labels=relationship.labels,
            updated_at=relationship.updated_at,
        )

    def _build_recent_logs(self) -> list[DirectorLogEntry]:
        events = list(reversed(self.world_runtime.get_recent_events(limit=12)))
        return [
            DirectorLogEntry(
                event_id=event.id,
                sequence_number=event.sequence_number,
                kind=event.kind.value,
                summary=event.summary,
                created_at=event.created_at,
                character_id=event.payload.get("character_id"),
                director_explanation=event.payload.get("director_explanation"),
            )
            for event in events
        ]

    def _truncate_message(self, content: str, *, limit: int = 96) -> str:
        normalized = " ".join(content.split())
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[: limit - 1]}…"
