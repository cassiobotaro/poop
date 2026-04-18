import ast

from poop.errors import ValidationError


class NoFreeFunctionsValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoFreeFunctionsVisitor().visit(tree)


class _NoFreeFunctionsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._class_depth: int = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_depth += 1
        self.generic_visit(node)
        self._class_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._class_depth == 0:
            raise ValidationError(
                "free functions are forbidden — define methods inside a class",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self._class_depth == 0:
            raise ValidationError(
                "free async functions are forbidden — define methods inside a class",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
