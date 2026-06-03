import ast

from poop.validators._op import make_op_validator

NoIsValidator = make_op_validator(
    ast.Compare,
    {
        ast.Is: "is operator is forbidden — use .is_none() for None checks or .is_identical(other) for identity",
        ast.IsNot: "is not operator is forbidden — use .not_none() for None checks or .not_identical(other) for identity",
    },
)
