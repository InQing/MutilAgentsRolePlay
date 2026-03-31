from app.infra.db.repositories import AsyncMessageRepository, AsyncMomentInteractionRepository
from app.relationship.service import RelationshipService
from app.social.models import (
    ConversationType,
    CreateMomentCommentRequest,
    CreateMomentInteractionRequest,
    CreateMomentLikeRequest,
    MessageRecord,
    MomentInteractionRecord,
    MomentInteractionType,
)
from app.social.service import SocialService
from app.world.events import WorldEvent, WorldEventKind
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


class MomentInteractionService:
    def __init__(
        self,
        *,
        social_service: SocialService,
        relationship_service: RelationshipService,
        world_runtime: WorldRuntimeService,
        world_persistence: WorldPersistenceService,
    ) -> None:
        self.social_service = social_service
        self.relationship_service = relationship_service
        self.world_runtime = world_runtime
        self.world_persistence = world_persistence

    async def list_interactions(self, *, moment_id: str) -> list[MomentInteractionRecord]:
        await self._get_moment_or_raise(moment_id=moment_id)
        async with self.social_service.database.session_factory() as session:
            repository = AsyncMomentInteractionRepository(session)
            return await repository.list_for_moment(moment_message_id=moment_id)

    async def create_comment(
        self,
        *,
        moment_id: str,
        request: CreateMomentCommentRequest,
    ) -> MomentInteractionRecord:
        moment = await self._get_moment_or_raise(moment_id=moment_id)

        async with self.social_service.database.session_factory() as session:
            async with session.begin():
                repository = AsyncMomentInteractionRepository(session)
                interaction = await repository.create_for_world(
                    world_id=self.social_service.world_id,
                    request=CreateMomentInteractionRequest(
                        moment_message_id=moment_id,
                        interaction_type=MomentInteractionType.COMMENT,
                        sender_id=request.sender_id,
                        content=request.content,
                        created_at=request.created_at,
                    ),
                )

        await self._record_interaction_side_effects(
            moment=moment,
            interaction=interaction,
        )
        return interaction

    async def create_like(
        self,
        *,
        moment_id: str,
        request: CreateMomentLikeRequest,
    ) -> MomentInteractionRecord:
        moment = await self._get_moment_or_raise(moment_id=moment_id)

        async with self.social_service.database.session_factory() as session:
            async with session.begin():
                repository = AsyncMomentInteractionRepository(session)
                existing_like = await repository.find_for_moment_sender_and_type(
                    moment_message_id=moment_id,
                    sender_id=request.sender_id,
                    interaction_type=MomentInteractionType.LIKE.value,
                )
                if existing_like is not None:
                    return existing_like

                interaction = await repository.create_for_world(
                    world_id=self.social_service.world_id,
                    request=CreateMomentInteractionRequest(
                        moment_message_id=moment_id,
                        interaction_type=MomentInteractionType.LIKE,
                        sender_id=request.sender_id,
                        created_at=request.created_at,
                    ),
                )

        await self._record_interaction_side_effects(
            moment=moment,
            interaction=interaction,
        )
        return interaction

    async def _get_moment_or_raise(self, *, moment_id: str) -> MessageRecord:
        async with self.social_service.database.session_factory() as session:
            repository = AsyncMessageRepository(session)
            moment = await repository.get_by_id(message_id=moment_id)

        if moment is None or moment.conversation_type != ConversationType.MOMENT:
            raise ValueError(f"Moment {moment_id} was not found.")
        return moment

    async def _record_interaction_side_effects(
        self,
        *,
        moment: MessageRecord,
        interaction: MomentInteractionRecord,
    ) -> None:
        updated_relationships = await self.relationship_service.apply_social_interaction(
            source_character_id=interaction.sender_id,
            target_character_ids=[moment.sender_id],
            interaction_kind=f"moment_{interaction.interaction_type.value}",
        )

        summary = (
            f"{interaction.sender_id} recorded a {interaction.interaction_type.value} "
            f"on {moment.sender_id}'s moment."
        )
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.MOMENT_INTERACTION_RECORDED,
                summary=summary,
                created_at=interaction.created_at,
                payload={
                    "character_id": interaction.sender_id,
                    "target_character_id": moment.sender_id,
                    "moment_message_id": moment.id,
                    "interaction_type": interaction.interaction_type.value,
                },
            )
        )
        if updated_relationships:
            self.world_runtime.record_event(
                WorldEvent(
                    world_id=self.world_runtime.world_id,
                    kind=WorldEventKind.RELATIONSHIP_UPDATED,
                    summary=(
                        f"{interaction.sender_id} and {moment.sender_id} relationship changed "
                        f"after a {interaction.interaction_type.value} on a moment."
                    ),
                    created_at=interaction.created_at,
                    payload={
                        "character_id": interaction.sender_id,
                        "target_character_id": moment.sender_id,
                        "moment_message_id": moment.id,
                        "interaction_type": interaction.interaction_type.value,
                        "updated_edge_count": str(len(updated_relationships)),
                    },
                )
            )

        await self.world_persistence.persist_runtime(self.world_runtime)
