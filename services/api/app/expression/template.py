from app.agent_runtime.types import ActionType
from app.expression.interfaces import ExpressionGenerator
from app.expression.models import ExpressionInput, ExpressionOutput


class TemplateExpressionGenerator(ExpressionGenerator):
    def generate(self, *, expression_input: ExpressionInput) -> ExpressionOutput:
        content = self._render_content(expression_input=expression_input)
        return ExpressionOutput(
            content=content,
            generator_kind="template",
            used_fallback=False,
        )

    def _render_content(self, *, expression_input: ExpressionInput) -> str:
        voice = self._resolve_voice(expression_input=expression_input)
        context_snippet = self._build_context_snippet(expression_input=expression_input)
        plan_snippet = f"我这边还在处理“{expression_input.current_plan_summary}”。"

        if expression_input.action_type == ActionType.GROUP_MESSAGE:
            if voice == "expressive":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"{plan_snippet} 我先来群里把气氛接上，看看大家现在聊到哪了。"
                )
            if voice == "reserved":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"{plan_snippet} 我先做个简短同步，看到需要我接的时候再继续。"
                )
            return (
                f"{expression_input.display_name}：{context_snippet}"
                f"{plan_snippet} 我先来群里报个到，顺手对一下大家现在的节奏。"
            )

        if expression_input.action_type == ActionType.PRIVATE_MESSAGE:
            target_hint = (
                f"给{expression_input.target_display_name}回个私聊。"
                if expression_input.target_display_name
                else "先把这条私聊接住。"
            )
            if voice == "expressive":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"{target_hint} 我刚看到这边的动静，先和你对一下，再继续忙手头安排。"
                )
            if voice == "reserved":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"{target_hint} 我先简短回复你，后面如果需要我再补充。"
                )
            return (
                f"{expression_input.display_name}：{context_snippet}"
                f"{target_hint} 我先跟你确认一下，免得信息在当前节奏里错过去。"
            )

        if expression_input.action_type == ActionType.MOMENT_POST:
            if voice == "expressive":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"今天整体节奏挺满的，不过“{expression_input.current_plan_summary}”正在往前推，"
                    "先留个动态，晚点应该会更热闹。"
                )
            if voice == "reserved":
                return (
                    f"{expression_input.display_name}：{context_snippet}"
                    f"先记录一下今天的进度，“{expression_input.current_plan_summary}”还在稳步推进。"
                )
            return (
                f"{expression_input.display_name}：{context_snippet}"
                f"今天先记一笔，“{expression_input.current_plan_summary}”还在推进，"
                "等后面有更明确的变化再继续补。"
            )

        return f"{expression_input.display_name} 暂时没有新的公开动作。"

    def _build_context_snippet(self, *, expression_input: ExpressionInput) -> str:
        recent_event = next(
            (
                event.summary
                for event in reversed(expression_input.recent_context)
                if event.summary
            ),
            None,
        )
        if recent_event is None:
            return ""

        if self._resolve_voice(expression_input=expression_input) == "reserved":
            return f"我刚留意到“{recent_event}”。 "
        return f"刚刚还在想着“{recent_event}”，"

    def _resolve_voice(self, *, expression_input: ExpressionInput) -> str:
        profile_text = " ".join(
            [
                expression_input.profile.personality,
                expression_input.profile.speaking_style,
                expression_input.profile.additional_notes,
            ]
        )
        expressive_keywords = ("外向", "热络", "主动", "破冰", "热情", "轻快")
        reserved_keywords = ("克制", "谨慎", "简短", "安静", "边界感", "直接")

        if (
            expression_input.interrupt_threshold >= 0.68
            or any(keyword in profile_text for keyword in reserved_keywords)
            or expression_input.emotion_state in {"focused", "steady", "tired"}
        ):
            return "reserved"

        if (
            expression_input.social_drive >= 0.72
            or any(keyword in profile_text for keyword in expressive_keywords)
            or expression_input.emotion_state in {"excited", "energized", "curious"}
        ):
            return "expressive"

        return "balanced"
