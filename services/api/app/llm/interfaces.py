from abc import ABC, abstractmethod
from typing import Any


class LLMClient(ABC):
    @abstractmethod
    def generate(self, *, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        raise NotImplementedError

