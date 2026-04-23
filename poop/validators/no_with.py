import ast

from poop.errors import ValidationError


class NoWithValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoWithVisitor().visit(tree)


class _NoWithVisitor(ast.NodeVisitor):
    def visit_With(self, node: ast.With) -> None:
        raise ValidationError(
            "with is forbidden — use With(lambda: cm()).do(lambda resource: body) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        raise ValidationError(
            "async with is forbidden — use With(lambda: cm()).do(lambda resource: body) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
