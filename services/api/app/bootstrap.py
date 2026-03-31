from app.agent_runtime.executor import AutonomousActionExecutor
from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.core.config import get_settings
from app.director.policies.member_director_hybrid import MemberDirectorHybridPolicy
from app.expression.service import CharacterExpressionService
from app.infra.cache.redis_client import RedisClientFactory
from app.infra.db.session import DatabaseManager
from app.llm.factory import build_llm_client
from app.llm.expression_service import LLMExpressionService
from app.relationship.service import RelationshipService
from app.social.interaction_service import MomentInteractionService
from app.social.service import SocialService
from app.world.persistence import WorldPersistenceService
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
        self.llm_client = build_llm_client(settings=settings)
        self.llm_expression_service = (
            LLMExpressionService(self.llm_client)
            if self.llm_client is not None
            else None
        )
        self.expression_generator = CharacterExpressionService(
            llm_expression_service=self.llm_expression_service
        )
        self.world_runtime = WorldRuntimeService(
            thinking_engine=self.thinking_engine,
            default_speed_multiplier=settings.world_default_speed_multiplier,
        )
        self.world_persistence = WorldPersistenceService(self.database)
        self.social_service = SocialService(
            self.database,
            world_id=self.world_runtime.world_id,
        )
        self.relationship_service = RelationshipService(
            self.database,
            world_id=self.world_runtime.world_id,
        )
        self.moment_interaction_service = MomentInteractionService(
            social_service=self.social_service,
            relationship_service=self.relationship_service,
            world_runtime=self.world_runtime,
            world_persistence=self.world_persistence,
        )
        self.autonomous_executor = AutonomousActionExecutor(
            runtime=self.world_runtime,
            social_gateway=self.social_service,
            expression_generator=self.expression_generator,
            relationship_service=self.relationship_service,
        )
        self.world_runtime.bootstrap_sample_world()


runtime_registry: RuntimeRegistry | None = None


def get_runtime_registry() -> RuntimeRegistry:
    global runtime_registry

    if runtime_registry is None:
        runtime_registry = RuntimeRegistry()
    return runtime_registry


def reset_runtime_registry() -> None:
    global runtime_registry
    runtime_registry = None
