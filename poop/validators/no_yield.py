import ast

from poop.validators._node import NodeValidator


class NoYieldValidator(NodeValidator):
    messages = {
        ast.Yield: "yield is forbidden — use collection messages do(block), map(block) instead",
        ast.YieldFrom: "yield from is forbidden — use collection messages do(block), map(block) instead",
    }
