from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MutilAgentsRolePlay API"
    env: str = "development"
    api_prefix: str = "/api"
    director_visibility_delay_seconds: int = 300
    database_url: str = "postgresql+asyncpg://marp:marp@localhost:5432/marp"
    redis_url: str = "redis://localhost:6379/0"
    scheduler_poll_seconds: int = 15
    world_default_speed_multiplier: float = 60.0
    db_auto_create_schema: bool = True

    model_config = SettingsConfigDict(
        env_prefix="MARP_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
