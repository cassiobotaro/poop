import ast

from poop.validators._op import OpValidator


class NoUnaryPlusValidator(OpValidator):
    node_type = ast.UnaryOp
    messages = {ast.UAdd: "unary plus is forbidden — write the value directly"}
