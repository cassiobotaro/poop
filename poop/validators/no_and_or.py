import ast

from poop.validators._op import make_op_validator

NoAndOrValidator = make_op_validator(
    ast.BoolOp,
    {
        ast.And: "and operator is forbidden — use .and_(lambda: ...) instead",
        ast.Or: "or operator is forbidden — use .or_(lambda: ...) instead",
    },
)
