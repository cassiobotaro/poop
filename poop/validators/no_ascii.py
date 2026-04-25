import ast

from poop.errors import ValidationError


class NoAsciiValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoAsciiVisitor().visit(tree)


class _NoAsciiVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "ascii":
            raise ValidationError(
                "ascii() is forbidden — use obj.ascii() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
