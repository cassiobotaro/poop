import ast

from poop.errors import ValidationError


class NoDirValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoDirVisitor().visit(tree)


class _NoDirVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "dir":
            raise ValidationError(
                "dir() is forbidden — use obj.dir() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
