import ast

from poop.errors import ValidationError


class NoReversedValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoReversedVisitor().visit(tree)


class _NoReversedVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "reversed":
            raise ValidationError(
                "reversed() is forbidden — use col.reversed() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
