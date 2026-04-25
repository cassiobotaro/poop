import ast

from poop.errors import ValidationError


class NoReprValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoReprVisitor().visit(tree)


class _NoReprVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "repr":
            raise ValidationError(
                "repr() is forbidden — use obj.repr() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
