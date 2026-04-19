import ast

from poop.errors import ValidationError


class NoUnaryMinusValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoUnaryMinusVisitor().visit(tree)


class _NoUnaryMinusVisitor(ast.NodeVisitor):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.USub) and not isinstance(node.operand, ast.Constant):
            raise ValidationError(
                "unary minus on expressions is forbidden — use .negated() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
