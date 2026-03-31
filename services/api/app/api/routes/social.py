from fastapi import APIRouter, HTTPException

from app.bootstrap import get_runtime_registry
from app.social.models import (
    ConversationSummary,
    CreateMessageRequest,
    CreateMomentCommentRequest,
    CreateMomentLikeRequest,
    CreateMomentRequest,
    CreatePrivateMessageRequest,
    MessageRecord,
    MomentInteractionRecord,
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


@router.get("/moments/{moment_id}/interactions", response_model=list[MomentInteractionRecord])
async def list_moment_interactions(moment_id: str) -> list[MomentInteractionRecord]:
    registry = get_runtime_registry()
    try:
        return await registry.moment_interaction_service.list_interactions(moment_id=moment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/moments/{moment_id}/comments", response_model=MomentInteractionRecord)
async def create_moment_comment(
    moment_id: str,
    request: CreateMomentCommentRequest,
) -> MomentInteractionRecord:
    registry = get_runtime_registry()
    try:
        return await registry.moment_interaction_service.create_comment(
            moment_id=moment_id,
            request=request,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/moments/{moment_id}/likes", response_model=MomentInteractionRecord)
async def create_moment_like(
    moment_id: str,
    request: CreateMomentLikeRequest,
) -> MomentInteractionRecord:
    registry = get_runtime_registry()
    try:
        return await registry.moment_interaction_service.create_like(
            moment_id=moment_id,
            request=request,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
