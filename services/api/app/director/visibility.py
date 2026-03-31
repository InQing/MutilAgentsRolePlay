from datetime import datetime, timedelta

from app.director.models import PermissionView, VisibilityMode
from app.world.events import WorldEvent, WorldEventKind


class DirectorVisibilityService:
    def __init__(self, *, delay_seconds: int) -> None:
        self.delay_seconds = delay_seconds

    def is_timestamp_visible(
        self,
        timestamp: datetime | None,
        *,
        visibility_mode: VisibilityMode,
        current_time: datetime,
    ) -> bool:
        if visibility_mode == VisibilityMode.REALTIME or timestamp is None:
            return True
        if visibility_mode == VisibilityMode.HIDDEN:
            return False
        if timestamp.tzinfo is None and current_time.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=current_time.tzinfo)
        if current_time.tzinfo is None and timestamp.tzinfo is not None:
            current_time = current_time.replace(tzinfo=timestamp.tzinfo)
        visible_after = current_time - timedelta(seconds=self.delay_seconds)
        return timestamp <= visible_after

    def is_moment_interaction_visible(
        self,
        *,
        timestamp: datetime | None,
        current_time: datetime,
    ) -> bool:
        return self.is_timestamp_visible(
            timestamp,
            visibility_mode=VisibilityMode.DELAYED,
            current_time=current_time,
        )

    def is_event_visible(
        self,
        event: WorldEvent,
        *,
        permissions: PermissionView,
        current_time: datetime,
    ) -> bool:
        if event.kind == WorldEventKind.DIRECTOR_NOTE:
            return True
        if event.kind == WorldEventKind.RELATIONSHIP_UPDATED:
            return self.is_timestamp_visible(
                event.created_at,
                visibility_mode=permissions.relationship_visibility,
                current_time=current_time,
            )
        if event.kind == WorldEventKind.MOMENT_INTERACTION_RECORDED:
            return self.is_moment_interaction_visible(
                timestamp=event.created_at,
                current_time=current_time,
            )
        return True
