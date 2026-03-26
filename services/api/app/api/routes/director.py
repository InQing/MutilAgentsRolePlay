from fastapi import APIRouter

from app.bootstrap import get_runtime_registry
from app.director.models import DirectorPanelState
from app.director.service import DirectorPanelService

router = APIRouter()


@router.get("/panel", response_model=DirectorPanelState)
async def get_director_panel() -> DirectorPanelState:
    registry = get_runtime_registry()
    service = DirectorPanelService(
        world_runtime=registry.world_runtime,
        social_service=registry.social_service,
        relationship_service=registry.relationship_service,
        permission_policy=registry.permission_policy,
        director_visibility_delay_seconds=registry.settings.director_visibility_delay_seconds,
    )
    return await service.get_panel_state()
