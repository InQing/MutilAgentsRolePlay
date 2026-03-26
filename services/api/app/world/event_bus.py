from collections import deque

from app.world.events import WorldEvent


class WorldEventBus:
    def __init__(self, *, history_limit: int = 50) -> None:
        self._queue: deque[WorldEvent] = deque()
        self._history: deque[WorldEvent] = deque(maxlen=history_limit)

    def publish(self, event: WorldEvent) -> None:
        self._queue.append(event)
        self._history.append(event)

    def drain(self) -> list[WorldEvent]:
        events = list(self._queue)
        self._queue.clear()
        return events

    def recent_summaries(self, *, limit: int = 10) -> list[str]:
        return [event.summary for event in list(self._history)[-limit:]]

