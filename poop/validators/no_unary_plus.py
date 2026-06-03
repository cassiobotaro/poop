import ast

from poop.validators._op import make_op_validator

NoUnaryPlusValidator = make_op_validator(
    ast.UnaryOp,
    {ast.UAdd: "unary plus is forbidden — write the value directly"},
)
