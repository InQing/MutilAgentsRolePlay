from fastapi import APIRouter, HTTPException

from app.bootstrap import get_runtime_registry
from app.director.models import DirectorPanelState, UpdateWorldSpeedRequest
from app.director.service import DirectorControlService, DirectorPanelService

router = APIRouter()


def _build_panel_service() -> DirectorPanelService:
    registry = get_runtime_registry()
    return DirectorPanelService(
        world_runtime=registry.world_runtime,
        social_service=registry.social_service,
        moment_interaction_service=registry.moment_interaction_service,
        relationship_service=registry.relationship_service,
        permission_policy=registry.permission_policy,
        director_visibility_delay_seconds=registry.settings.director_visibility_delay_seconds,
    )


def _build_control_service() -> DirectorControlService:
    registry = get_runtime_registry()
    return DirectorControlService(
        world_runtime=registry.world_runtime,
        world_persistence=registry.world_persistence,
        permission_policy=registry.permission_policy,
    )


@router.get("/panel", response_model=DirectorPanelState)
async def get_director_panel() -> DirectorPanelState:
    service = _build_panel_service()
    return await service.get_panel_state()


@router.post("/pause", response_model=DirectorPanelState)
async def pause_world() -> DirectorPanelState:
    control_service = _build_control_service()
    panel_service = _build_panel_service()
    try:
        await control_service.pause_world()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return await panel_service.get_panel_state()


@router.post("/resume", response_model=DirectorPanelState)
async def resume_world() -> DirectorPanelState:
    control_service = _build_control_service()
    panel_service = _build_panel_service()
    try:
        await control_service.resume_world()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return await panel_service.get_panel_state()


@router.post("/speed", response_model=DirectorPanelState)
async def update_world_speed(request: UpdateWorldSpeedRequest) -> DirectorPanelState:
    control_service = _build_control_service()
    panel_service = _build_panel_service()
    try:
        await control_service.set_world_speed(speed_multiplier=request.speed_multiplier)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return await panel_service.get_panel_state()
