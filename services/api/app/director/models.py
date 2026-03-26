from enum import StrEnum

from pydantic import BaseModel


class VisibilityMode(StrEnum):
    REALTIME = "realtime"
    DELAYED = "delayed"
    HIDDEN = "hidden"


class PermissionView(BaseModel):
    private_chat_visibility: VisibilityMode
    plan_visibility: VisibilityMode
    relationship_visibility: VisibilityMode
    can_inject_events: bool
    can_control_world: bool


class DirectorPanelState(BaseModel):
    permissions: PermissionView
    recent_logs: list[str]

