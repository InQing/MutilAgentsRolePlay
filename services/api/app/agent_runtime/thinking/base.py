from abc import ABC, abstractmethod

from app.agent_runtime.types import ActionDecision, DirectorExplanation, VisibleContext
from app.character.models import CharacterState


class ThinkingEngine(ABC):
    @abstractmethod
    def decide(
        self,
        *,
        character_state: CharacterState,
        visible_context: VisibleContext,
    ) -> tuple[ActionDecision, DirectorExplanation]:
        raise NotImplementedError

