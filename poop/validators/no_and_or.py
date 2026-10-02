import ast

from poop.validators._op import OpValidator


class NoAndOrValidator(OpValidator):
    node_type = ast.BoolOp
    messages = {
        ast.And: "and operator is forbidden — use .and_(lambda: ...) instead",
        ast.Or: "or operator is forbidden — use .or_(lambda: ...) instead",
    }
