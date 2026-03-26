from fastapi import APIRouter

from app.bootstrap import get_runtime_registry
from app.world.models import WorldState

router = APIRouter()


@router.get("/state", response_model=WorldState)
async def get_world_state() -> WorldState:
    registry = get_runtime_registry()
    return registry.world_runtime.get_world_state()


@router.post("/advance", response_model=WorldState)
async def advance_world(seconds: int = 15) -> WorldState:
    registry = get_runtime_registry()
    due_tasks, _ = registry.world_runtime.advance(seconds=seconds)
    await registry.autonomous_executor.execute_due_tasks(tasks=due_tasks)
    await registry.world_persistence.persist_runtime(registry.world_runtime)
    return registry.world_runtime.get_world_state()
