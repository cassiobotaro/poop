import ast

from poop.errors import ValidationError


class NoLoopsValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoLoopsVisitor().visit(tree)


class _NoLoopsVisitor(ast.NodeVisitor):
    def visit_For(self, node: ast.For) -> None:
        raise ValidationError(
            "for loops are forbidden — use recursion or message passing instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_While(self, node: ast.While) -> None:
        raise ValidationError(
            "while loops are forbidden — use recursion or message passing instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        raise ValidationError(
            "async for loops are forbidden — use recursion or message passing instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
