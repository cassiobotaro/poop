import ast

from poop.errors import ValidationError


class NoAnyValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAnyVisitor().visit(tree)


class _NoAnyVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "any":
            raise ValidationError(
                "any() is forbidden — use col.any(block) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
