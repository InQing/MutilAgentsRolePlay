from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.core.config import get_settings
from app.director.policies.member_director_hybrid import MemberDirectorHybridPolicy
from app.infra.cache.redis_client import RedisClientFactory
from app.infra.db.session import DatabaseManager
from app.world.service import WorldRuntimeService


class RuntimeRegistry:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.thinking_engine = StateDrivenThinkingEngine()
        self.permission_policy = MemberDirectorHybridPolicy(
            director_delay_seconds=settings.director_visibility_delay_seconds
        )
        self.database = DatabaseManager(settings.database_url)
        self.redis = RedisClientFactory(settings.redis_url)
        self.world_runtime = WorldRuntimeService(
            thinking_engine=self.thinking_engine,
            default_speed_multiplier=settings.world_default_speed_multiplier,
        )
        self.world_runtime.bootstrap_sample_world()


runtime_registry: RuntimeRegistry | None = None


def get_runtime_registry() -> RuntimeRegistry:
    global runtime_registry

    if runtime_registry is None:
        runtime_registry = RuntimeRegistry()
    return runtime_registry
