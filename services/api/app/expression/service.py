from app.expression.interfaces import ExpressionGenerator
from app.expression.models import ExpressionInput, ExpressionOutput
from app.expression.template import TemplateExpressionGenerator
from app.llm.expression_service import LLMExpressionService


class CharacterExpressionService(ExpressionGenerator):
    def __init__(
        self,
        *,
        template_generator: TemplateExpressionGenerator | None = None,
        llm_expression_service: LLMExpressionService | None = None,
    ) -> None:
        self.template_generator = template_generator or TemplateExpressionGenerator()
        self.llm_expression_service = llm_expression_service

    def generate(self, *, expression_input: ExpressionInput) -> ExpressionOutput:
        if self.llm_expression_service is None:
            return self.template_generator.generate(expression_input=expression_input)

        try:
            content = self.llm_expression_service.generate_content(
                expression_input=expression_input
            )
            return ExpressionOutput(
                content=content,
                generator_kind="llm",
                used_fallback=False,
            )
        except Exception:
            fallback = self.template_generator.generate(expression_input=expression_input)
            return fallback.model_copy(update={"used_fallback": True})
