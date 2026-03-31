import asyncio

from app.character.models import CharacterState
from app.director.models import (
    DirectorCharacterSnapshot,
    DirectorConversationPreview,
    DirectorLogEntry,
    DirectorMomentInteractionEntry,
    DirectorPanelState,
    DirectorRelationshipEdge,
)
from app.director.visibility import DirectorVisibilityService
from app.plan.models import PlanItem, PlanStatus
from app.relationship.models import RelationshipSnapshot
from app.relationship.service import RelationshipService
from app.social.interaction_service import MomentInteractionService
from app.social.models import ConversationSummary, MessageRecord, MomentInteractionRecord
from app.social.service import SocialService
from app.world.events import RuntimeTask, WorldEvent, WorldEventKind
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


class DirectorPanelService:
    def __init__(
        self,
        *,
        world_runtime: WorldRuntimeService,
        social_service: SocialService,
        moment_interaction_service: MomentInteractionService,
        relationship_service: RelationshipService,
        permission_policy,
        director_visibility_delay_seconds: int,
    ) -> None:
        self.world_runtime = world_runtime
        self.social_service = social_service
        self.moment_interaction_service = moment_interaction_service
        self.relationship_service = relationship_service
        self.permission_policy = permission_policy
        self.director_visibility_delay_seconds = director_visibility_delay_seconds
        self.visibility = DirectorVisibilityService(
            delay_seconds=director_visibility_delay_seconds
        )

    async def get_panel_state(self) -> DirectorPanelState:
        permissions = self.permission_policy.describe_view()
        clock = self.world_runtime.clock.snapshot()
        characters = self.world_runtime.list_characters()
        plans = self.world_runtime.list_plans()
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
            characters=self._build_character_snapshots(
                characters,
                plans,
                pending_tasks,
                permissions=permissions,
                current_time=clock.now,
            ),
            relationships=await self._build_relationship_edges(
                character_lookup,
                permissions=permissions,
                current_time=clock.now,
            ),
            conversations=await self._build_conversation_previews(
                character_lookup,
                permissions=permissions,
                current_time=clock.now,
            ),
            moment_interactions=await self._build_moment_interactions(
                character_lookup,
                current_time=clock.now,
            ),
            recent_logs=self._build_recent_logs(
                permissions=permissions,
                current_time=clock.now,
            ),
        )

    def _build_character_snapshots(
        self,
        characters: list[CharacterState],
        plans: list[PlanItem],
        pending_tasks: list[RuntimeTask],
        *,
        permissions,
        current_time,
    ) -> list[DirectorCharacterSnapshot]:
        next_task_by_character: dict[str, RuntimeTask] = {}
        active_plan_by_character: dict[str, PlanItem] = {}

        for plan in sorted(
            plans,
            key=lambda item: (item.next_run_at, item.priority, item.id),
        ):
            if plan.status != PlanStatus.ACTIVE or plan.character_id in active_plan_by_character:
                continue
            active_plan_by_character[plan.character_id] = plan

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
            active_plan = active_plan_by_character.get(character.id)
            next_task = next_task_by_character.get(character.id)
            plan_visible = self.visibility.is_timestamp_visible(
                active_plan.updated_at if active_plan is not None else None,
                visibility_mode=permissions.plan_visibility,
                current_time=current_time,
            )
            snapshots.append(
                DirectorCharacterSnapshot(
                    id=character.id,
                    display_name=character.display_name,
                    emotion_state=character.emotion_state,
                    current_plan_summary=(
                        character.current_plan_summary
                        if plan_visible
                        else "导演视角延迟可见"
                    ),
                    social_drive=character.social_drive,
                    interrupt_threshold=character.interrupt_threshold,
                    next_task_type=next_task.task_type if plan_visible and next_task is not None else None,
                    next_task_intent=(
                        next_task.payload.get("intent")
                        if plan_visible and next_task is not None
                        else None
                    ),
                    next_task_run_at=next_task.run_at if plan_visible and next_task is not None else None,
                )
            )
        return snapshots

    async def _build_conversation_previews(
        self,
        character_lookup: dict[str, CharacterState],
        *,
        permissions,
        current_time,
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
                    permissions=permissions,
                    current_time=current_time,
                )
            )
        return previews

    async def _build_relationship_edges(
        self,
        character_lookup: dict[str, CharacterState],
        *,
        permissions,
        current_time,
    ) -> list[DirectorRelationshipEdge]:
        relationships = await self.relationship_service.list_relationships()
        return [
            self._build_relationship_edge(
                relationship=relationship,
                character_lookup=character_lookup,
            )
            for relationship in relationships
            if self.visibility.is_timestamp_visible(
                relationship.updated_at,
                visibility_mode=permissions.relationship_visibility,
                current_time=current_time,
            )
        ]

    def _build_conversation_preview(
        self,
        *,
        conversation: ConversationSummary,
        messages: list[MessageRecord],
        character_lookup: dict[str, CharacterState],
        permissions,
        current_time,
    ) -> DirectorConversationPreview:
        visible_messages = messages
        if conversation.conversation_type.value == "private":
            visible_messages = [
                message
                for message in messages
                if self.visibility.is_timestamp_visible(
                    message.created_at,
                    visibility_mode=permissions.private_chat_visibility,
                    current_time=current_time,
                )
            ]
        latest_message = visible_messages[-1] if visible_messages else None
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

    async def _build_moment_interactions(
        self,
        character_lookup: dict[str, CharacterState],
        *,
        current_time,
    ) -> list[DirectorMomentInteractionEntry]:
        moment_messages = await self.social_service.list_messages(
            conversation_id="conv-moments"
        )
        if not moment_messages:
            return []

        interaction_results = await asyncio.gather(
            *[
                self.moment_interaction_service.list_interactions(moment_id=moment.id)
                for moment in moment_messages
            ]
        )

        entries: list[DirectorMomentInteractionEntry] = []
        for moment, interactions in zip(moment_messages, interaction_results, strict=False):
            entries.extend(
                self._build_moment_interaction_entries_for_moment(
                    moment=moment,
                    interactions=interactions,
                    character_lookup=character_lookup,
                    current_time=current_time,
                )
            )

        entries.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return entries[:12]

    def _build_moment_interaction_entries_for_moment(
        self,
        *,
        moment: MessageRecord,
        interactions: list[MomentInteractionRecord],
        character_lookup: dict[str, CharacterState],
        current_time,
    ) -> list[DirectorMomentInteractionEntry]:
        target_moment_sender = character_lookup.get(moment.sender_id)
        entries: list[DirectorMomentInteractionEntry] = []
        for interaction in interactions:
            if not self.visibility.is_moment_interaction_visible(
                timestamp=interaction.created_at,
                current_time=current_time,
            ):
                continue

            actor = character_lookup.get(interaction.sender_id)
            entries.append(
                DirectorMomentInteractionEntry(
                    id=interaction.id,
                    interaction_type=interaction.interaction_type.value,
                    actor_id=interaction.sender_id,
                    actor_display_name=actor.display_name if actor is not None else interaction.sender_id,
                    target_moment_id=moment.id,
                    target_moment_preview=self._truncate_message(moment.content, limit=72),
                    target_moment_sender_id=moment.sender_id,
                    target_moment_sender_name=(
                        target_moment_sender.display_name
                        if target_moment_sender is not None
                        else moment.sender_id
                    ),
                    content=interaction.content,
                    created_at=interaction.created_at,
                )
            )
        return entries

    def _build_recent_logs(
        self,
        *,
        permissions,
        current_time,
    ) -> list[DirectorLogEntry]:
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
            if self.visibility.is_event_visible(
                event,
                permissions=permissions,
                current_time=current_time,
            )
        ]

    def _truncate_message(self, content: str, *, limit: int = 96) -> str:
        normalized = " ".join(content.split())
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[: limit - 1]}…"


class DirectorControlService:
    def __init__(
        self,
        *,
        world_runtime: WorldRuntimeService,
        world_persistence: WorldPersistenceService,
        permission_policy,
    ) -> None:
        self.world_runtime = world_runtime
        self.world_persistence = world_persistence
        self.permission_policy = permission_policy

    async def pause_world(self) -> None:
        self._assert_can_control_world()
        clock = self.world_runtime.clock.pause()
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.DIRECTOR_NOTE,
                summary="Director paused the world runtime.",
                created_at=clock.now,
                payload={"control_action": "pause"},
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)

    async def resume_world(self) -> None:
        self._assert_can_control_world()
        clock = self.world_runtime.clock.resume()
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.DIRECTOR_NOTE,
                summary="Director resumed the world runtime.",
                created_at=clock.now,
                payload={"control_action": "resume"},
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)

    async def set_world_speed(self, *, speed_multiplier: float) -> None:
        self._assert_can_control_world()
        clock = self.world_runtime.clock.set_speed(speed_multiplier)
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.DIRECTOR_NOTE,
                summary=f"Director set world speed to {speed_multiplier:.2f}.",
                created_at=clock.now,
                payload={
                    "control_action": "set_speed",
                    "speed_multiplier": f"{speed_multiplier:.2f}",
                },
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)

    def _assert_can_control_world(self) -> None:
        permission_view = self.permission_policy.describe_view()
        if not permission_view.can_control_world:
            raise PermissionError("Director control is disabled by the current permission policy.")
