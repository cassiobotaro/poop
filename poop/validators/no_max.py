import ast

from poop.errors import ValidationError


class NoMaxValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoMaxVisitor().visit(tree)


class _NoMaxVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "max":
            raise ValidationError(
                "max() is forbidden — use a.max(b) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
