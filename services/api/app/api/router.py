from fastapi import APIRouter

from app.api.routes.director import router as director_router
from app.api.routes.health import router as health_router
from app.api.routes.social import router as social_router
from app.api.routes.world import router as world_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(world_router, prefix="/world", tags=["world"])
api_router.include_router(director_router, prefix="/director", tags=["director"])
api_router.include_router(social_router, prefix="/social", tags=["social"])
