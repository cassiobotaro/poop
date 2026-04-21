import ast

from poop.errors import ValidationError


class NoPowValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoPowVisitor().visit(tree)


class _NoPowVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "pow":
            raise ValidationError(
                "pow() is forbidden — use a.pow(b) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
