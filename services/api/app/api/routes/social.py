from fastapi import APIRouter

from app.bootstrap import get_runtime_registry
from app.social.models import (
    ConversationSummary,
    CreateMessageRequest,
    CreateMomentRequest,
    CreatePrivateMessageRequest,
    MessageRecord,
)

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations() -> list[ConversationSummary]:
    registry = get_runtime_registry()
    return await registry.social_service.list_conversations()


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRecord])
async def list_messages(conversation_id: str) -> list[MessageRecord]:
    registry = get_runtime_registry()
    return await registry.social_service.list_messages(conversation_id=conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageRecord)
async def create_message(
    conversation_id: str,
    request: CreateMessageRequest,
) -> MessageRecord:
    registry = get_runtime_registry()
    payload = request.model_copy(update={"conversation_id": conversation_id})
    return await registry.social_service.create_message(payload)


@router.post("/private-messages", response_model=MessageRecord)
async def create_private_message(request: CreatePrivateMessageRequest) -> MessageRecord:
    registry = get_runtime_registry()
    return await registry.social_service.create_private_message(request)


@router.post("/moments", response_model=MessageRecord)
async def create_moment(request: CreateMomentRequest) -> MessageRecord:
    registry = get_runtime_registry()
    return await registry.social_service.create_moment(request)
