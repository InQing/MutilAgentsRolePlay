from app.expression.models import ExpressionInput
from app.llm.expression_prompting import (
    build_expression_system_prompt,
    build_expression_user_prompt,
    parse_expression_content,
)
from app.llm.interfaces import LLMClient


class LLMExpressionService:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def generate_content(self, *, expression_input: ExpressionInput) -> str:
        payload = self.llm_client.generate(
            system_prompt=build_expression_system_prompt(),
            user_prompt=build_expression_user_prompt(expression_input=expression_input),
        )
        content = parse_expression_content(payload)
        if not content:
            raise ValueError("llm expression payload returned empty content")
        return content
