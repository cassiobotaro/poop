import ast

from poop.validators._node import make_node_validator

NoYieldValidator = make_node_validator(
    {
        ast.Yield: "yield is forbidden — use collection messages do(block), map(block) instead",
        ast.YieldFrom: "yield from is forbidden — use collection messages do(block), map(block) instead",
    }
)
