from fastapi import APIRouter, HTTPException

from app.bootstrap import get_runtime_registry
from app.character.models import (
    CreateCharacterRequest,
    DeleteCharacterResponse,
    EditableCharacter,
    UpdateCharacterRequest,
)
from app.character.service import CharacterManagementService

router = APIRouter()


def _build_character_service() -> CharacterManagementService:
    registry = get_runtime_registry()
    return CharacterManagementService(
        world_runtime=registry.world_runtime,
        world_persistence=registry.world_persistence,
        relationship_service=registry.relationship_service,
    )


@router.get("", response_model=list[EditableCharacter])
async def list_characters() -> list[EditableCharacter]:
    service = _build_character_service()
    return await service.list_characters()


@router.put("/{character_id}", response_model=EditableCharacter)
async def update_character(
    character_id: str,
    request: UpdateCharacterRequest,
) -> EditableCharacter:
    service = _build_character_service()
    try:
        return await service.update_character(
            character_id=character_id,
            request=request,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=EditableCharacter)
async def create_character(request: CreateCharacterRequest) -> EditableCharacter:
    service = _build_character_service()
    return await service.create_character(request=request)


@router.delete("/{character_id}", response_model=DeleteCharacterResponse)
async def delete_character(character_id: str) -> DeleteCharacterResponse:
    service = _build_character_service()
    try:
        return await service.delete_character(character_id=character_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
