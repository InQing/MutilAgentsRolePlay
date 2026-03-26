from fastapi import APIRouter

from app.bootstrap import get_runtime_registry
from app.world.models import WorldState

router = APIRouter()


@router.get("/state", response_model=WorldState)
def get_world_state() -> WorldState:
    registry = get_runtime_registry()
    return registry.world_runtime.get_world_state()


@router.post("/advance", response_model=WorldState)
def advance_world(seconds: int = 15) -> WorldState:
    registry = get_runtime_registry()
    registry.world_runtime.advance(seconds=seconds)
    return registry.world_runtime.get_world_state()
