import ast

from poop.errors import ValidationError


class NoTryValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoTryVisitor().visit(tree)


class _NoTryVisitor(ast.NodeVisitor):
    def visit_Try(self, node: ast.Try) -> None:
        raise ValidationError(
            "try/except is forbidden — use on:do: messaging instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_TryStar(self, node: ast.TryStar) -> None:
        raise ValidationError(
            "try/except* is forbidden — use on:do: messaging instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
