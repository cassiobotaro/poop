import ast

from poop.errors import ValidationError


class NoHashValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoHashVisitor().visit(tree)


class _NoHashVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "hash":
            raise ValidationError(
                "hash() is forbidden — use obj.hash() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
