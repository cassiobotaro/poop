import ast

from poop.validators._op import OpValidator


class NoIsValidator(OpValidator):
    node_type = ast.Compare
    messages = {
        ast.Is: "is operator is forbidden — use .is_none() for None checks or .is_identical(other) for identity",
        ast.IsNot: "is not operator is forbidden — use .not_none() for None checks or .not_identical(other) for identity",
    }
