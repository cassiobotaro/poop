import ast

from poop.errors import ValidationError


class NoMinValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoMinVisitor().visit(tree)


class _NoMinVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "min":
            raise ValidationError(
                "min() is forbidden — use a.min(b) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
