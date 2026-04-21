import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"bin", "hex", "oct"})


class NoBinValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoBinVisitor().visit(tree)


class _NoBinVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            name = node.func.id
            raise ValidationError(
                f"{name}() is forbidden — use n.{name}() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
