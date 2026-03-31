from app.expression.models import ExpressionInput


def build_expression_system_prompt() -> str:
    return (
        "你负责为多角色社交模拟系统生成角色表达。"
        "只输出角色最终会发出的文本，不要解释，不要暴露思维链，"
        "并保持语气贴合角色画像、当前情绪和当前计划。"
    )


def build_expression_user_prompt(*, expression_input: ExpressionInput) -> str:
    recent_context = (
        "\n".join(f"- {event.summary}" for event in expression_input.recent_context)
        if expression_input.recent_context
        else "- 当前没有额外最近事件"
    )
    target_line = (
        f"目标对象：{expression_input.target_display_name or expression_input.target_id}"
        if expression_input.target_id or expression_input.target_display_name
        else "目标对象：无"
    )
    return (
        f"角色名：{expression_input.display_name}\n"
        f"角色背景：{expression_input.profile.identity_and_background}\n"
        f"角色性格：{expression_input.profile.personality}\n"
        f"说话风格：{expression_input.profile.speaking_style}\n"
        f"外在气质：{expression_input.profile.appearance_and_presence}\n"
        f"补充备注：{expression_input.profile.additional_notes or '无'}\n"
        f"当前情绪：{expression_input.emotion_state}\n"
        f"当前计划：{expression_input.current_plan_summary}\n"
        f"社交驱动力：{expression_input.social_drive:.2f}\n"
        f"打断阈值：{expression_input.interrupt_threshold:.2f}\n"
        f"动作类型：{expression_input.action_type.value}\n"
        f"决策原因：{expression_input.decision_reason}\n"
        f"{target_line}\n"
        f"最近上下文：\n{recent_context}\n"
        "请生成一条符合该角色状态的中文消息，长度控制在一到三句。"
    )


def parse_expression_content(payload: dict) -> str:
    if isinstance(payload.get("content"), str):
        return payload["content"].strip()
    if isinstance(payload.get("text"), str):
        return payload["text"].strip()
    if isinstance(payload.get("message"), str):
        return payload["message"].strip()
    raise ValueError("llm expression payload does not contain content")
