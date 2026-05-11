import ast

from poop.validators._node import make_node_validator

NoLoopsValidator = make_node_validator(
    {
        ast.For: "for loops are forbidden — use col.do(block) instead",
        ast.While: "while loops are forbidden — use (lambda: cond).while_true(lambda: body) or (lambda: cond).while_false(lambda: body) instead",
        ast.AsyncFor: "async for loops are forbidden — use col.do(block) instead",
    }
)
