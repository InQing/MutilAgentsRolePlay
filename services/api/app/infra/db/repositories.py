from collections.abc import Sequence

from app.character.models import CharacterState
from app.world.events import RuntimeTask, WorldEvent


class CharacterRepository:
    def __init__(self) -> None:
        self._characters: dict[str, CharacterState] = {}

    def save_many(self, characters: Sequence[CharacterState]) -> None:
        for character in characters:
            self._characters[character.id] = character

    def list_all(self) -> list[CharacterState]:
        return list(self._characters.values())


class WorldEventRepository:
    def __init__(self) -> None:
        self._events: list[WorldEvent] = []

    def append(self, event: WorldEvent) -> None:
        self._events.append(event)

    def recent_summaries(self, *, limit: int = 10) -> list[str]:
        return [event.summary for event in self._events[-limit:]]


class SchedulerRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, RuntimeTask] = {}

    def save(self, task: RuntimeTask) -> None:
        self._tasks[task.id] = task

    def remove(self, task_id: str) -> None:
        self._tasks.pop(task_id, None)

    def list_all(self) -> list[RuntimeTask]:
        return list(self._tasks.values())

