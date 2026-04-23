import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"iter", "next", "aiter", "anext"})


class NoIterValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIterVisitor().visit(tree)


class _NoIterVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — use col.do(block) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
