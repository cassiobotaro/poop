import ast

from poop.validators._op import make_op_validator

NoInvertValidator = make_op_validator(
    ast.UnaryOp,
    {ast.Invert: "bitwise invert operator is forbidden — use .bit_invert() instead"},
)
