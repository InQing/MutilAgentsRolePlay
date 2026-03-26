from app.infra.db.repositories import (
    AsyncConversationRepository,
    AsyncMessageRepository,
)
from app.infra.db.session import DatabaseManager
from app.social.interfaces import AutonomousSocialGateway
from app.social.models import (
    ConversationSummary,
    CreateMessageRequest,
    CreateMomentRequest,
    CreatePrivateMessageRequest,
    MessageRecord,
)


class SocialService(AutonomousSocialGateway):
    def __init__(self, database: DatabaseManager, *, world_id: str) -> None:
        self.database = database
        self.world_id = world_id

    async def ensure_defaults(self) -> None:
        async with self.database.session_factory() as session:
            async with session.begin():
                repository = AsyncConversationRepository(session)
                await repository.ensure_defaults(world_id=self.world_id)

    async def list_conversations(self) -> list[ConversationSummary]:
        async with self.database.session_factory() as session:
            repository = AsyncConversationRepository(session)
            return await repository.list_for_world(world_id=self.world_id)

    async def list_messages(self, *, conversation_id: str) -> list[MessageRecord]:
        async with self.database.session_factory() as session:
            repository = AsyncMessageRepository(session)
            return await repository.list_for_conversation(conversation_id=conversation_id)

    async def create_message(self, request: CreateMessageRequest) -> MessageRecord:
        async with self.database.session_factory() as session:
            async with session.begin():
                repository = AsyncMessageRepository(session)
                return await repository.create_for_world(
                    world_id=self.world_id,
                    request=request,
                )

    async def post_group_message(self, *, sender_id: str, content: str) -> MessageRecord:
        return await self.create_message(
            CreateMessageRequest(
                conversation_id="conv-general",
                conversation_type="group",
                sender_id=sender_id,
                content=content,
            )
        )

    async def post_private_message(
        self,
        *,
        sender_id: str,
        target_id: str,
        content: str,
        created_at=None,
    ) -> MessageRecord:
        async with self.database.session_factory() as session:
            async with session.begin():
                conversation_repository = AsyncConversationRepository(session)
                message_repository = AsyncMessageRepository(session)
                conversation = await conversation_repository.ensure_private_conversation(
                    world_id=self.world_id,
                    participant_ids=[sender_id, target_id],
                )
                request_payload = {
                    "conversation_id": conversation.id,
                    "conversation_type": conversation.conversation_type,
                    "sender_id": sender_id,
                    "content": content,
                    "target_id": target_id,
                }
                if created_at is not None:
                    request_payload["created_at"] = created_at
                return await message_repository.create_for_world(
                    world_id=self.world_id,
                    request=CreateMessageRequest(**request_payload),
                )

    async def post_moment(
        self,
        *,
        sender_id: str,
        content: str,
        mentions: list[str] | None = None,
        created_at=None,
    ) -> MessageRecord:
        request_payload = {
            "conversation_id": "conv-moments",
            "conversation_type": "moment",
            "sender_id": sender_id,
            "content": content,
            "mentions": mentions or [],
        }
        if created_at is not None:
            request_payload["created_at"] = created_at
        return await self.create_message(
            CreateMessageRequest(**request_payload)
        )

    async def create_private_message(self, request: CreatePrivateMessageRequest) -> MessageRecord:
        return await self.post_private_message(
            sender_id=request.sender_id,
            target_id=request.target_id,
            content=request.content,
            created_at=request.created_at,
        )

    async def create_moment(self, request: CreateMomentRequest) -> MessageRecord:
        return await self.post_moment(
            sender_id=request.sender_id,
            content=request.content,
            mentions=request.mentions,
            created_at=request.created_at,
        )
