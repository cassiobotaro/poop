import ast

from poop.validators._op import make_op_validator

NoInValidator = make_op_validator(
    ast.Compare,
    {
        ast.In: "in operator is forbidden — use col.includes(x) instead",
        ast.NotIn: "not in operator is forbidden — use col.includes(x).not_() instead",
    },
)
