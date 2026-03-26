from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.bootstrap import get_runtime_registry
from app.core.config import get_settings
from app.infra.db.initializer import initialize_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    registry = get_runtime_registry()
    if settings.db_auto_create_schema:
        await initialize_database(registry.database)
    await registry.world_persistence.bootstrap_or_load(registry.world_runtime)
    await registry.social_service.ensure_defaults()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MutilAgentsRolePlay API is running"}
