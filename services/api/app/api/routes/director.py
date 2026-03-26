from fastapi import APIRouter

from app.bootstrap import get_runtime_registry
from app.director.models import DirectorPanelState

router = APIRouter()


@router.get("/panel", response_model=DirectorPanelState)
def get_director_panel() -> DirectorPanelState:
    registry = get_runtime_registry()
    permissions = registry.permission_policy.describe_view()
    logs = [
        "Director mode uses delayed visibility for private conversations.",
        "ThinkingEngine defaults to StateDrivenThinkingEngine.",
        "WorkflowRunner and LLMClient are reserved for future integrations.",
        f"Scheduler poll interval target: {registry.settings.scheduler_poll_seconds} seconds.",
    ]
    return DirectorPanelState(permissions=permissions, recent_logs=logs)
