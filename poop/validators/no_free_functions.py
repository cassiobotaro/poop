import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors


class NoFreeFunctionsValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_NoFreeFunctionsVisitor(), tree)


class _NoFreeFunctionsVisitor(ErrorCollector):
    def __init__(self) -> None:
        super().__init__()
        # A function is a method only when it is a *direct* statement of a class
        # body. Counting class nesting was not enough: a `def` nested inside a
        # method sits at `class_depth > 0` yet its parent is the method, not the
        # class, so it slipped through as a receiver-less named local function.
        # Smalltalk has blocks (lambdas), not named local functions — so anything
        # whose direct parent is not a ClassDef is rejected, module level and
        # method-nested alike.
        self._method_nodes: set[ast.AST] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._method_nodes.add(stmt)
        self.generic_visit(node)

    def _reject_if_free(self, node: ast.AST, kind: str) -> None:
        if node not in self._method_nodes:
            self.report(
                f"free {kind} are forbidden — define methods inside a class "
                "(use a lambda for a local block)",
                node,
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._reject_if_free(node, "functions")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._reject_if_free(node, "async functions")
