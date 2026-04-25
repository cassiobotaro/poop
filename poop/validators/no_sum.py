import ast

from poop.errors import ValidationError


class NoSumValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSumVisitor().visit(tree)


class _NoSumVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "sum":
            raise ValidationError(
                "sum() is forbidden — use col.sum() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
