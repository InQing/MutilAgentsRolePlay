from datetime import datetime, timedelta, timezone

from app.world.models import ClockState


class WorldClock:
    def __init__(self, *, speed_multiplier: float = 60.0) -> None:
        self._now = datetime.now(timezone.utc)
        self._speed_multiplier = speed_multiplier
        self._paused = False

    def snapshot(self) -> ClockState:
        return ClockState(
            now=self._now,
            speed_multiplier=self._speed_multiplier,
            paused=self._paused,
        )

    def load_snapshot(self, clock_state: ClockState) -> ClockState:
        self._now = clock_state.now
        self._speed_multiplier = clock_state.speed_multiplier
        self._paused = clock_state.paused
        return self.snapshot()

    def tick(self, seconds: int) -> ClockState:
        if not self._paused:
            self._now += timedelta(seconds=seconds * self._speed_multiplier)
        return self.snapshot()

    def pause(self) -> ClockState:
        self._paused = True
        return self.snapshot()

    def resume(self) -> ClockState:
        self._paused = False
        return self.snapshot()

    def set_speed(self, speed_multiplier: float) -> ClockState:
        self._speed_multiplier = speed_multiplier
        return self.snapshot()
