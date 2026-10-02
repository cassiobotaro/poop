import ast

from poop.validators._op import OpValidator

# Unary `-` is allowed only on numeric literals. `bool` is excluded by
# design: even though Python treats `bool` as a subclass of `int`, POOP
# does not — Boolean is its own type and `-True` makes no sense in the
# Smalltalk-flavoured semantics POOP is going for.
_NUMERIC_LITERAL_TYPES = (int, float, complex)


def _is_numeric_literal(node: ast.expr) -> bool:
    if not isinstance(node, ast.Constant):
        return False
    return type(node.value) in _NUMERIC_LITERAL_TYPES


class NoUnaryMinusValidator(OpValidator):
    node_type = ast.UnaryOp
    messages = {
        ast.USub: "unary minus is allowed only on numeric literals "
        "(int, float, complex) — use .negated() instead"
    }

    def allow(self, node: ast.UnaryOp) -> bool:
        return _is_numeric_literal(node.operand)
