import asyncio

from app.agent_runtime.executor import AutonomousActionExecutor
from app.agent_runtime.thinking.state_driven import StateDrivenThinkingEngine
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
