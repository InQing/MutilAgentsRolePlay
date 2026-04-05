import re

from app.agent_runtime.types import ActionType
from app.expression.models import ExpressionInput


def build_expression_system_prompt() -> str:
    return "\n".join(
        [
            "你是多角色社交模拟系统里的表达层，只负责把既定动作写成角色真正会发出去的中文正文。",
            "硬性要求：",
            "1. 只输出最终正文，不要解释、分析、道歉、复述要求，不要暴露思维链。",
            "2. 不要输出角色名、冒号、标题、引号、项目符号、Markdown、代码块或舞台说明。",
            "3. 语气必须贴合角色画像、当前情绪、当前计划和最近上下文，不要写成通用客服腔或万能鸡汤。",
            "4. 保持自然、口语化、像社交场景里真的会发出去的话，长度控制在一到三句。",
            "5. 信息不足时宁可写得简洁，也不要编造设定或补充未给出的事实。",
        ]
    )


def _build_recent_context_block(expression_input: ExpressionInput) -> str:
    if not expression_input.recent_context:
        return "- 当前没有额外最近事件"

    lines: list[str] = []
    for event in expression_input.recent_context:
        tags: list[str] = [event.kind]
        if event.is_directed_at_character:
            tags.append("directed_at_character")
        tag_prefix = f"[{', '.join(tags)}]"
        lines.append(f"- {tag_prefix} {event.summary}")
    return "\n".join(lines)


def _build_action_instruction(expression_input: ExpressionInput) -> str:
    if expression_input.action_type == ActionType.GROUP_MESSAGE:
        return (
            "这是群聊发言。要像角色在公共群里顺手发出的一条消息，"
            "可以自然带动话题，但不要写成汇报模板或主持人口播。"
        )
    if expression_input.action_type == ActionType.PRIVATE_MESSAGE:
        target_name = expression_input.target_display_name or expression_input.target_id or "对方"
        return (
            f"这是发给 {target_name} 的私聊。语气要像一对一交流，"
            "允许自然称呼对方，但不要写成正式信件。"
        )
    if expression_input.action_type == ActionType.MOMENT_POST:
        return (
            "这是角色发到朋友圈/动态流的一条内容。要像独立发布的动态，"
            "不要写成对某个人的直接回复，也不要带聊天抬头。"
        )
    return "这是角色要发出的一条社交文本。"


def _build_state_guidance(expression_input: ExpressionInput) -> str:
    drive_hint = (
        "社交驱动力偏高，可以更主动、更愿意抛话题。"
        if expression_input.social_drive >= 0.7
        else "社交驱动力偏低，表达应更克制，避免无谓铺垫。"
        if expression_input.social_drive <= 0.35
        else "社交驱动力中等，表达保持自然推进。"
    )
    interrupt_hint = (
        "打断阈值偏高，表达应更谨慎，不要显得过分闯入。"
        if expression_input.interrupt_threshold >= 0.7
        else "打断阈值偏低，可以更自然地接话或主动切入。"
        if expression_input.interrupt_threshold <= 0.35
        else "打断阈值中等，表达保持适度分寸。"
    )
    return f"{drive_hint}{interrupt_hint}"


def build_expression_user_prompt(*, expression_input: ExpressionInput) -> str:
    recent_context = _build_recent_context_block(expression_input)
    target_line = (
        f"目标对象：{expression_input.target_display_name or expression_input.target_id}"
        if expression_input.target_id or expression_input.target_display_name
        else "目标对象：无"
    )
    return "\n".join(
        [
            "请根据以下角色资料生成本次最终发送内容：",
            f"角色名：{expression_input.display_name}",
            f"角色背景：{expression_input.profile.identity_and_background}",
            f"角色性格：{expression_input.profile.personality}",
            f"说话风格：{expression_input.profile.speaking_style}",
            f"外在气质：{expression_input.profile.appearance_and_presence}",
            f"补充备注：{expression_input.profile.additional_notes or '无'}",
            f"当前情绪：{expression_input.emotion_state}",
            f"当前计划：{expression_input.current_plan_summary}",
            f"社交驱动力：{expression_input.social_drive:.2f}",
            f"打断阈值：{expression_input.interrupt_threshold:.2f}",
            f"动作类型：{expression_input.action_type.value}",
            f"决策原因：{expression_input.decision_reason}",
            f"{target_line}",
            f"动作约束：{_build_action_instruction(expression_input)}",
            f"状态提示：{_build_state_guidance(expression_input)}",
            "最近上下文：",
            recent_context,
            "输出要求：",
            "1. 只输出最终正文，不要再写“好的”“以下是”“这条消息是”等引导语。",
            "2. 不要添加角色名、冒号、引号、标题、括号动作说明或任何额外标签。",
            "3. 不要把“决策原因”原样复述出来，要把它转成自然表达。",
            "4. 用中文输出，控制在一到三句，优先短而自然。",
        ]
    )


def _strip_code_fence(content: str) -> str:
    match = re.fullmatch(r"```(?:[\w-]+)?\s*(.*?)\s*```", content, flags=re.DOTALL)
    return match.group(1).strip() if match else content


def _strip_wrapping_quotes(content: str) -> str:
    quote_pairs = [
        ("“", "”"),
        ("‘", "’"),
        ("「", "」"),
        ("『", "』"),
        ('"', '"'),
        ("'", "'"),
    ]
    stripped = content.strip()
    changed = True
    while changed:
        changed = False
        for left, right in quote_pairs:
            if stripped.startswith(left) and stripped.endswith(right) and len(stripped) >= 2:
                stripped = stripped[len(left) : -len(right)].strip()
                changed = True
    return stripped


def _strip_meta_prefix(content: str, *, expression_input: ExpressionInput | None) -> str:
    stripped = content.strip()
    generic_prefix_pattern = re.compile(
        r"^(?:好的[，, ]*)?(?:以下是|这是|这里是)?(?:一条)?"
        r"(?:符合.*?的)?(?:中文)?(?:最终)?"
        r"(?:群聊消息|私聊消息|朋友圈文案|动态文案|动态|回复|消息内容|消息|输出内容|输出|正文)"
        r"[：:]\s*"
    )
    stripped = generic_prefix_pattern.sub("", stripped, count=1)

    if expression_input is not None:
        name_pattern = re.escape(expression_input.display_name)
        stripped = re.sub(
            rf"^(?:【{name_pattern}】|\[{name_pattern}\]|{name_pattern})[：:]\s*",
            "",
            stripped,
            count=1,
        )
    return stripped.strip()


def _collapse_whitespace(content: str) -> str:
    lines = [line.strip() for line in content.replace("\r\n", "\n").split("\n")]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines).strip()


def parse_expression_content(
    payload: dict,
    *,
    expression_input: ExpressionInput | None = None,
) -> str:
    if isinstance(payload.get("content"), str):
        raw_content = payload["content"]
    elif isinstance(payload.get("text"), str):
        raw_content = payload["text"]
    elif isinstance(payload.get("message"), str):
        raw_content = payload["message"]
    else:
        raise ValueError("llm expression payload does not contain content")

    content = _collapse_whitespace(raw_content)
    content = _strip_code_fence(content)
    content = _collapse_whitespace(content)
    content = _strip_meta_prefix(content, expression_input=expression_input)
    content = _strip_wrapping_quotes(content)
    content = _collapse_whitespace(content)
    return content
