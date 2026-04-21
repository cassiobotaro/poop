import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"exit", "quit"})


class NoExitValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoExitVisitor().visit(tree)


class _NoExitVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — no POOP equivalent",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
