import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector


class NoFreeFunctionsValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        visitor = _NoFreeFunctionsVisitor()
        visitor.visit(tree)
        return visitor.errors


class _NoFreeFunctionsVisitor(ErrorCollector):
    def __init__(self) -> None:
        super().__init__()
        self._class_depth: int = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._class_depth == 0:
            self.report(
                "free functions are forbidden — define methods inside a class",
                node,
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._class_depth == 0:
            self.report(
                "free async functions are forbidden — define methods inside a class",
                node,
            )
        self.generic_visit(node)
