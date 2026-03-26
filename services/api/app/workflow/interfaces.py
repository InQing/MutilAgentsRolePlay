from abc import ABC, abstractmethod
from typing import Any


class WorkflowRunner(ABC):
    @abstractmethod
    def run(self, workflow_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

