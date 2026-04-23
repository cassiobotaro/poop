import ast

from poop.errors import ValidationError


class NoYieldValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoYieldVisitor().visit(tree)


class _NoYieldVisitor(ast.NodeVisitor):
    def visit_Yield(self, node: ast.Yield) -> None:
        raise ValidationError(
            "yield is forbidden — use collection messages do(block), map(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        raise ValidationError(
            "yield from is forbidden — use collection messages do(block), map(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
