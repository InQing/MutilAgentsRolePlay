import asyncio

from app.agent_runtime.executor import AutonomousActionExecutor
from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
from app.expression.interfaces import ExpressionGenerator
from app.expression.models import ExpressionInput, ExpressionOutput
from app.relationship.models import RelationshipSnapshot
from app.social.interfaces import AutonomousSocialGateway
from app.social.models import ConversationType, MessageRecord
from app.world.events import RuntimeTask
from app.world.service import WorldRuntimeService


class FakeSocialGateway(AutonomousSocialGateway):
    def __init__(self) -> None:
        self.messages: list[MessageRecord] = []

    async def post_group_message(self, *, sender_id: str, content: str) -> MessageRecord:
        message = MessageRecord(
            conversation_id="conv-general",
            conversation_type=ConversationType.GROUP,
            sender_id=sender_id,
            content=content,
        )
        self.messages.append(message)
        return message

    async def post_private_message(
        self,
        *,
        sender_id: str,
        target_id: str,
        content: str,
    ) -> MessageRecord:
        message = MessageRecord(
            conversation_id="conv-private-test",
            conversation_type=ConversationType.PRIVATE,
            sender_id=sender_id,
            content=content,
            target_id=target_id,
        )
        self.messages.append(message)
        return message

    async def post_moment(self, *, sender_id: str, content: str) -> MessageRecord:
        message = MessageRecord(
            conversation_id="conv-moments",
            conversation_type=ConversationType.MOMENT,
            sender_id=sender_id,
            content=content,
        )
        self.messages.append(message)
        return message


class CaptureExpressionGenerator(ExpressionGenerator):
    def __init__(self) -> None:
        self.inputs: list[ExpressionInput] = []

    def generate(self, *, expression_input: ExpressionInput) -> ExpressionOutput:
        self.inputs.append(expression_input)
        return ExpressionOutput(
            content="测试消息",
            generator_kind="capture",
            used_fallback=False,
        )


class FakeRelationshipService:
    def __init__(self, relationships: list[RelationshipSnapshot]) -> None:
        self.relationships = relationships

    async def list_relationships_for_character(
        self,
        *,
        character_id: str,
    ) -> list[RelationshipSnapshot]:
        return [
            relationship
            for relationship in self.relationships
            if relationship.source_character_id == character_id
        ]

    async def apply_social_interaction(
        self,
        *,
        source_character_id: str,
        target_character_ids: list[str],
        interaction_kind: str,
    ) -> list[RelationshipSnapshot]:
        return []


def test_autonomous_executor_writes_group_message_for_scheduled_check_in() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()
    gateway = FakeSocialGateway()
    executor = AutonomousActionExecutor(runtime=runtime, social_gateway=gateway)

    task = RuntimeTask(
        world_id=runtime.world_id,
        task_type="character_plan_tick",
        run_at=runtime.clock.snapshot().now,
        payload={"character_id": "char-001", "intent": "check_group_chat"},
        priority=1,
    )

    executions = asyncio.run(executor.execute_due_tasks(tasks=[task]))

    assert len(executions) == 1
    assert executions[0].message is not None
    assert executions[0].message.conversation_id == "conv-general"
    assert "群里" in executions[0].message.content
    assert any(
        event.kind.value == "action_executed"
        for event in runtime.get_recent_events(limit=10)
    )


def test_autonomous_executor_generates_distinct_group_message_styles_for_different_characters() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()
    gateway = FakeSocialGateway()
    executor = AutonomousActionExecutor(runtime=runtime, social_gateway=gateway)

    tasks = [
        RuntimeTask(
            world_id=runtime.world_id,
            task_type="character_plan_tick",
            run_at=runtime.clock.snapshot().now,
            payload={"character_id": "char-001", "intent": "check_group_chat"},
            priority=1,
        ),
        RuntimeTask(
            world_id=runtime.world_id,
            task_type="character_plan_tick",
            run_at=runtime.clock.snapshot().now,
            payload={"character_id": "char-002", "intent": "check_group_chat"},
            priority=1,
        ),
    ]

    executions = asyncio.run(executor.execute_due_tasks(tasks=tasks))

    assert len(executions) == 2
    assert executions[0].message is not None
    assert executions[1].message is not None
    first_content = executions[0].message.content
    second_content = executions[1].message.content
    assert first_content != second_content
    assert "群里" in first_content
    assert "简短同步" in second_content


def test_autonomous_executor_only_passes_character_owned_relationships_to_expression_layer() -> None:
    runtime = WorldRuntimeService(
        thinking_engine=StateDrivenThinkingEngine(),
        default_speed_multiplier=60.0,
    )
    runtime.bootstrap_sample_world()
    gateway = FakeSocialGateway()
    capture_generator = CaptureExpressionGenerator()
    executor = AutonomousActionExecutor(
        runtime=runtime,
        social_gateway=gateway,
        expression_generator=capture_generator,
        relationship_service=FakeRelationshipService(
            [
                RelationshipSnapshot(
                    source_character_id="char-001",
                    target_character_id="char-002",
                    affinity=0.48,
                    labels=["recent_private_contact"],
                ),
                RelationshipSnapshot(
                    source_character_id="char-002",
                    target_character_id="char-001",
                    affinity=0.18,
                    labels=["recent_group_contact"],
                ),
            ]
        ),
    )

    task = RuntimeTask(
        world_id=runtime.world_id,
        task_type="character_plan_tick",
        run_at=runtime.clock.snapshot().now,
        payload={"character_id": "char-001", "intent": "check_group_chat"},
        priority=1,
    )

    asyncio.run(executor.execute_due_tasks(tasks=[task]))

    assert len(capture_generator.inputs) == 1
    relationship_context = capture_generator.inputs[0].relationship_context
    assert len(relationship_context) == 1
    assert relationship_context[0].target_character_id == "char-002"
    assert relationship_context[0].target_display_name == "许遥"
    assert relationship_context[0].labels == ["recent_private_contact"]
