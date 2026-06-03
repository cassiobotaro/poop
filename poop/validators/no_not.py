import ast

from poop.validators._op import make_op_validator

NoNotValidator = make_op_validator(
    ast.UnaryOp,
    {ast.Not: "not operator is forbidden — use .not_() instead"},
)
