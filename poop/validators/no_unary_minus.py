import ast

from poop.validators._op import make_op_validator

# Unary `-` is allowed only on numeric literals. `bool` is excluded by
# design: even though Python treats `bool` as a subclass of `int`, POOP
# does not — Boolean is its own type and `-True` makes no sense in the
# Smalltalk-flavoured semantics POOP is going for.
_NUMERIC_LITERAL_TYPES = (int, float, complex)


def _is_numeric_literal(node: ast.expr) -> bool:
    if not isinstance(node, ast.Constant):
        return False
    return type(node.value) in _NUMERIC_LITERAL_TYPES


NoUnaryMinusValidator = make_op_validator(
    ast.UnaryOp,
    {
        ast.USub: "unary minus is allowed only on numeric literals "
        "(int, float, complex) — use .negated() instead"
    },
    allow=lambda node: _is_numeric_literal(node.operand),
)
