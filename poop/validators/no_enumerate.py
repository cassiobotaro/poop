import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"enumerate", "zip"})


class NoEnumerateValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoEnumerateVisitor().visit(tree)


class _NoEnumerateVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — use collection messages map(block), reduce(init, block) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
