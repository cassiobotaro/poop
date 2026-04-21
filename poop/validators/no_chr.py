import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"chr", "ord"})


class NoChrValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoChrVisitor().visit(tree)


class _NoChrVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            name = node.func.id
            raise ValidationError(
                f"{name}() is forbidden — use obj.{name}() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
