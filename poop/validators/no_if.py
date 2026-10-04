import ast

from poop.validators._node import NodeValidator


class NoIfValidator(NodeValidator):
    messages = {
        ast.If: "if statements are forbidden — use cond.if_true(block) / cond.if_false(block) / cond.if_true_if_false(t, f) instead",
        ast.IfExp: "ternary if expressions are forbidden — use cond.if_true_if_false(t_block, f_block) instead",
    }
