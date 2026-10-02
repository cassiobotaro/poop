import ast

from poop.validators._op import OpValidator


class NoNotValidator(OpValidator):
    node_type = ast.UnaryOp
    messages = {ast.Not: "not operator is forbidden — use .not_() instead"}
