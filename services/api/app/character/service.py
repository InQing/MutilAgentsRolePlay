from app.character.models import (
    CreateCharacterRequest,
    DeleteCharacterResponse,
    EditableCharacter,
    UpdateCharacterRequest,
    build_character_state,
    build_editable_character,
)
from app.relationship.service import RelationshipService
from app.world.events import WorldEvent, WorldEventKind
from app.world.persistence import WorldPersistenceService
from app.world.service import WorldRuntimeService


class CharacterManagementService:
    def __init__(
        self,
        *,
        world_runtime: WorldRuntimeService,
        world_persistence: WorldPersistenceService,
        relationship_service: RelationshipService,
    ) -> None:
        self.world_runtime = world_runtime
        self.world_persistence = world_persistence
        self.relationship_service = relationship_service

    async def list_characters(self) -> list[EditableCharacter]:
        return [
            build_editable_character(character)
            for character in sorted(
                self.world_runtime.list_characters(),
                key=lambda item: (item.display_name, item.id),
            )
        ]

    async def update_character(
        self,
        *,
        character_id: str,
        request: UpdateCharacterRequest,
    ) -> EditableCharacter:
        existing = self.world_runtime.get_character(character_id)
        if existing is None:
            raise ValueError(f"character {character_id} was not found")

        updated_character = build_character_state(
            character_id=character_id,
            payload=request,
        )
        self.world_runtime.update_character(character=updated_character)
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.CHARACTER_UPDATED,
                summary=f"Character {updated_character.display_name} was updated from the character manager.",
                created_at=self.world_runtime.clock.snapshot().now,
                payload={"character_id": updated_character.id},
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)
        return build_editable_character(updated_character)

    async def create_character(self, *, request: CreateCharacterRequest) -> EditableCharacter:
        created_character = build_character_state(payload=request)
        self.world_runtime.add_character(character=created_character)
        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.CHARACTER_CREATED,
                summary=f"Character {created_character.display_name} joined the active world.",
                created_at=self.world_runtime.clock.snapshot().now,
                payload={"character_id": created_character.id},
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)
        await self.relationship_service.ensure_defaults(
            characters=self.world_runtime.list_characters()
        )
        return build_editable_character(created_character)

    async def delete_character(self, *, character_id: str) -> DeleteCharacterResponse:
        removed_character = self.world_runtime.remove_character(character_id=character_id)
        if removed_character is None:
            raise ValueError(f"character {character_id} was not found")

        self.world_runtime.record_event(
            WorldEvent(
                world_id=self.world_runtime.world_id,
                kind=WorldEventKind.CHARACTER_DELETED,
                summary=f"Character {removed_character.display_name} was removed from the active world.",
                created_at=self.world_runtime.clock.snapshot().now,
                payload={"character_id": removed_character.id},
            )
        )
        await self.world_persistence.persist_runtime(self.world_runtime)
        await self.relationship_service.delete_character_relationships(
            character_id=removed_character.id
        )
        return DeleteCharacterResponse(character_id=removed_character.id)
