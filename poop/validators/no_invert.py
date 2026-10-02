import ast

from poop.validators._op import OpValidator


class NoInvertValidator(OpValidator):
    node_type = ast.UnaryOp
    messages = {
        ast.Invert: "bitwise invert operator is forbidden — use .bit_invert() instead"
    }
