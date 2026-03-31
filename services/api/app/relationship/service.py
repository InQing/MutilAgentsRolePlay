from dataclasses import dataclass
from datetime import datetime, timezone

from app.character.models import CharacterState
from app.infra.db.repositories import AsyncRelationshipRepository
from app.infra.db.session import DatabaseManager
from app.relationship.models import RelationshipSnapshot


@dataclass(frozen=True)
class RelationshipInteractionRule:
    source_delta: float
    reciprocal_delta: float
    label: str


class RelationshipService:
    def __init__(self, database: DatabaseManager, *, world_id: str) -> None:
        self.database = database
        self.world_id = world_id

    async def ensure_defaults(self, *, characters: list[CharacterState]) -> None:
        async with self.database.session_factory() as session:
            async with session.begin():
                repository = AsyncRelationshipRepository(session)
                await repository.ensure_defaults_for_world(
                    world_id=self.world_id,
                    character_ids=[character.id for character in characters],
                )

    async def list_relationships(self) -> list[RelationshipSnapshot]:
        async with self.database.session_factory() as session:
            repository = AsyncRelationshipRepository(session)
            return await repository.list_for_world(world_id=self.world_id)

    async def apply_social_interaction(
        self,
        *,
        source_character_id: str,
        target_character_ids: list[str],
        interaction_kind: str,
    ) -> list[RelationshipSnapshot]:
        unique_target_ids = sorted(
            {
                target_id
                for target_id in target_character_ids
                if target_id and target_id != source_character_id
            }
        )
        if not unique_target_ids:
            return []

        rule = self._resolve_interaction_rule(interaction_kind)
        updated_at = datetime.now(timezone.utc)
        updated_relationships: list[RelationshipSnapshot] = []

        async with self.database.session_factory() as session:
            async with session.begin():
                repository = AsyncRelationshipRepository(session)
                for target_id in unique_target_ids:
                    updated_relationships.append(
                        await repository.apply_affinity_delta(
                            world_id=self.world_id,
                            source_character_id=source_character_id,
                            target_character_id=target_id,
                            delta=rule.source_delta,
                            label=rule.label,
                            updated_at=updated_at,
                        )
                    )
                    updated_relationships.append(
                        await repository.apply_affinity_delta(
                            world_id=self.world_id,
                            source_character_id=target_id,
                            target_character_id=source_character_id,
                            delta=rule.reciprocal_delta,
                            label=rule.label,
                            updated_at=updated_at,
                        )
                    )

        return updated_relationships

    def _resolve_interaction_rule(self, interaction_kind: str) -> RelationshipInteractionRule:
        rules = {
            "private_message": RelationshipInteractionRule(
                source_delta=0.08,
                reciprocal_delta=0.04,
                label="recent_private_contact",
            ),
            "group_message": RelationshipInteractionRule(
                source_delta=0.03,
                reciprocal_delta=0.015,
                label="recent_group_contact",
            ),
            "moment_post": RelationshipInteractionRule(
                source_delta=0.02,
                reciprocal_delta=0.01,
                label="recent_moment_activity",
            ),
            "moment_comment": RelationshipInteractionRule(
                source_delta=0.05,
                reciprocal_delta=0.025,
                label="recent_moment_reply",
            ),
            "moment_like": RelationshipInteractionRule(
                source_delta=0.015,
                reciprocal_delta=0.008,
                label="recent_moment_reaction",
            ),
        }
        return rules.get(
            interaction_kind,
            RelationshipInteractionRule(
                source_delta=0.01,
                reciprocal_delta=0.005,
                label="recent_social_activity",
            ),
        )
