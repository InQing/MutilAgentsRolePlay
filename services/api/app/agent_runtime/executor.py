from dataclasses import dataclass

from app.agent_runtime.types import ActionDecision, ActionType, DirectorExplanation, VisibleContext, VisibleEvent
from app.character.models import CharacterState
from app.relationship.service import RelationshipService
from app.social.interfaces import AutonomousSocialGateway
from app.social.models import MessageRecord
from app.world.events import RuntimeTask, WorldEvent, WorldEventKind
from app.world.service import WorldRuntimeService


@dataclass
class ExecutedAutonomousAction:
    task_id: str
    decision: ActionDecision
    explanation: DirectorExplanation
    message: MessageRecord | None


class AutonomousActionExecutor:
    def __init__(
        self,
        *,
        runtime: WorldRuntimeService,
        social_gateway: AutonomousSocialGateway,
        relationship_service: RelationshipService | None = None,
    ) -> None:
        self.runtime = runtime
        self.social_gateway = social_gateway
        self.relationship_service = relationship_service

    async def execute_due_tasks(
        self,
        *,
        tasks: list[RuntimeTask],
    ) -> list[ExecutedAutonomousAction]:
        executions: list[ExecutedAutonomousAction] = []

        for task in tasks:
            character = self.runtime.get_character(task.payload.get("character_id"))
            if character is None:
                self.runtime.record_event(
                    WorldEvent(
                        world_id=self.runtime.world_id,
                        kind=WorldEventKind.ACTION_SKIPPED,
                        summary=(
                            f"Skipped task {task.task_type} because the target character "
                            "was not found."
                        ),
                        created_at=self.runtime.clock.snapshot().now,
                        payload=task.payload,
                    )
                )
                continue

            visible_context = self.runtime.build_visible_context(character=character, task=task)
            decision, explanation = self.runtime.thinking_engine.decide(
                character_state=character,
                visible_context=visible_context,
            )
            message = await self._execute_decision(
                character=character,
                decision=decision,
                explanation=explanation,
            )
            self.runtime.schedule_follow_up_task(character=character, previous_decision=decision)
            executions.append(
                ExecutedAutonomousAction(
                    task_id=task.id,
                    decision=decision,
                    explanation=explanation,
                    message=message,
                )
            )

        return executions

    async def _execute_decision(
        self,
        *,
        character: CharacterState,
        decision: ActionDecision,
        explanation: DirectorExplanation,
    ) -> MessageRecord | None:
        if decision.action_type == ActionType.IGNORE:
            self.runtime.record_event(
                WorldEvent(
                    world_id=self.runtime.world_id,
                    kind=WorldEventKind.ACTION_SKIPPED,
                    summary=(
                        f"{character.display_name} skipped acting and stayed with the current plan."
                    ),
                    created_at=self.runtime.clock.snapshot().now,
                    payload={"character_id": character.id, "reason": decision.reason},
                )
            )
            return None

        content = self._render_content(character=character, decision=decision)

        if decision.action_type == ActionType.GROUP_MESSAGE:
            message = await self.social_gateway.post_group_message(
                sender_id=character.id,
                content=content,
            )
        elif decision.action_type == ActionType.PRIVATE_MESSAGE:
            target_id = decision.target_id or self.runtime.pick_peer_character_id(exclude_id=character.id)
            if target_id is None:
                self.runtime.record_event(
                    WorldEvent(
                        world_id=self.runtime.world_id,
                        kind=WorldEventKind.ACTION_SKIPPED,
                        summary=(
                            f"{character.display_name} wanted to send a private message but "
                            "no valid target was available."
                        ),
                        created_at=self.runtime.clock.snapshot().now,
                        payload={"character_id": character.id},
                    )
                )
                return None
            message = await self.social_gateway.post_private_message(
                sender_id=character.id,
                target_id=target_id,
                content=content,
            )
        elif decision.action_type == ActionType.MOMENT_POST:
            message = await self.social_gateway.post_moment(
                sender_id=character.id,
                content=content,
            )
        else:
            self.runtime.record_event(
                WorldEvent(
                    world_id=self.runtime.world_id,
                    kind=WorldEventKind.ACTION_SKIPPED,
                    summary=(
                        f"{character.display_name} produced unsupported action "
                        f"{decision.action_type.value} in the current runtime."
                    ),
                    created_at=self.runtime.clock.snapshot().now,
                    payload={"character_id": character.id},
                )
            )
            return None

        self.runtime.record_event(
            WorldEvent(
                world_id=self.runtime.world_id,
                kind=WorldEventKind.ACTION_EXECUTED,
                summary=(
                    f"{character.display_name} executed {decision.action_type.value} "
                    f"and wrote a new message."
                ),
                created_at=self.runtime.clock.snapshot().now,
                payload={
                    "character_id": character.id,
                    "message_id": message.id,
                    "conversation_id": message.conversation_id,
                    "director_explanation": explanation.summary,
                },
            )
        )
        await self._apply_relationship_updates(
            character=character,
            decision=decision,
            message=message,
        )
        return message

    def _render_content(
        self,
        *,
        character: CharacterState,
        decision: ActionDecision,
    ) -> str:
        if decision.action_type == ActionType.GROUP_MESSAGE:
            return (
                f"{character.display_name}：我刚在处理“{character.current_plan_summary}”，"
                "先来群里冒个泡，看看大家现在在聊什么。"
            )
        if decision.action_type == ActionType.PRIVATE_MESSAGE:
            return (
                f"{character.display_name}：我刚看到你的消息了。"
                "我这边还在忙手头的安排，不过可以先和你对一下。"
            )
        if decision.action_type == ActionType.MOMENT_POST:
            return (
                f"{character.display_name}：今天的节奏有点满，不过“{character.current_plan_summary}”"
                "正在慢慢推进，晚点应该会更热闹。"
            )
        return f"{character.display_name} 暂时没有新的公开动作。"

    async def _apply_relationship_updates(
        self,
        *,
        character: CharacterState,
        decision: ActionDecision,
        message: MessageRecord,
    ) -> None:
        if self.relationship_service is None:
            return

        target_ids = self._resolve_relationship_targets(
            actor_id=character.id,
            decision=decision,
            message=message,
        )
        if not target_ids:
            return

        updated_relationships = await self.relationship_service.apply_social_interaction(
            source_character_id=character.id,
            target_character_ids=target_ids,
            interaction_kind=decision.action_type.value,
        )
        if not updated_relationships:
            return

        target_names = []
        for target_id in target_ids:
            target_character = self.runtime.get_character(target_id)
            if target_character is not None:
                target_names.append(target_character.display_name)

        self.runtime.record_event(
            WorldEvent(
                world_id=self.runtime.world_id,
                kind=WorldEventKind.RELATIONSHIP_UPDATED,
                summary=(
                    f"{character.display_name} 的关系图谱已根据最近一次"
                    f"{decision.action_type.value} 更新。"
                ),
                created_at=self.runtime.clock.snapshot().now,
                payload={
                    "character_id": character.id,
                    "target_character_id": target_ids[0],
                    "relationship_targets": ", ".join(target_names),
                    "updated_edge_count": str(len(updated_relationships)),
                },
            )
        )

    def _resolve_relationship_targets(
        self,
        *,
        actor_id: str,
        decision: ActionDecision,
        message: MessageRecord,
    ) -> list[str]:
        if decision.action_type == ActionType.PRIVATE_MESSAGE:
            return [target_id for target_id in [message.target_id or decision.target_id] if target_id]

        if decision.action_type in {ActionType.GROUP_MESSAGE, ActionType.MOMENT_POST}:
            return [
                character.id
                for character in self.runtime.list_characters()
                if character.id != actor_id
            ]

        return []
