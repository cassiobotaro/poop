import ast

from poop.errors import ValidationError


class NoIfValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIfVisitor().visit(tree)


class _NoIfVisitor(ast.NodeVisitor):
    def visit_If(self, node: ast.If) -> None:
        raise ValidationError(
            "if statements are forbidden — use cond.if_true(block) / cond.if_false(block) / cond.if_true_if_false(t, f) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_IfExp(self, node: ast.IfExp) -> None:
        raise ValidationError(
            "ternary if expressions are forbidden — use cond.if_true_if_false(t_block, f_block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
