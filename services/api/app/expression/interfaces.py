from abc import ABC, abstractmethod

from app.expression.models import ExpressionInput, ExpressionOutput


class ExpressionGenerator(ABC):
    @abstractmethod
    def generate(self, *, expression_input: ExpressionInput) -> ExpressionOutput:
        raise NotImplementedError
