import ast

from poop.errors import ValidationError


class NoDivmodValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoDivmodVisitor().visit(tree)


class _NoDivmodVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "divmod":
            raise ValidationError(
                "divmod() is forbidden — use a.divmod(b) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
