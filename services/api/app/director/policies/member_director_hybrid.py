from app.director.models import PermissionView, VisibilityMode
from app.director.policies.base import PermissionPolicy


class MemberDirectorHybridPolicy(PermissionPolicy):
    def __init__(self, *, director_delay_seconds: int) -> None:
        self.director_delay_seconds = director_delay_seconds

    def describe_view(self) -> PermissionView:
        return PermissionView(
            private_chat_visibility=VisibilityMode.DELAYED,
            plan_visibility=VisibilityMode.DELAYED,
            relationship_visibility=VisibilityMode.DELAYED,
            can_inject_events=True,
            can_control_world=True,
        )

