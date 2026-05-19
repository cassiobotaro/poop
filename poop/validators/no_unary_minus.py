import ast

from poop.errors import ValidationError

# Unary `-` is allowed only on numeric literals. `bool` is excluded by
# design: even though Python treats `bool` as a subclass of `int`, POOP
# does not — Boolean is its own type and `-True` makes no sense in the
# Smalltalk-flavoured semantics POOP is going for.
_NUMERIC_LITERAL_TYPES = (int, float, complex)


class NoUnaryMinusValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoUnaryMinusVisitor().visit(tree)


class _NoUnaryMinusVisitor(ast.NodeVisitor):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if isinstance(node.op, ast.USub) and not _is_numeric_literal(node.operand):
            raise ValidationError(
                "unary minus is allowed only on numeric literals "
                "(int, float, complex) — use .negated() instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)


def _is_numeric_literal(node: ast.expr) -> bool:
    if not isinstance(node, ast.Constant):
        return False
    return type(node.value) in _NUMERIC_LITERAL_TYPES
