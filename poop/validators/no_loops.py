import ast

from poop.validators._node import make_node_validator

NoLoopsValidator = make_node_validator(
    {
        ast.For: "for loops are forbidden — use col.do(block) instead",
        ast.While: "while loops are forbidden — use (lambda: cond).while_true(lambda: body) or (lambda: cond).while_false(lambda: body) instead",
        # Reachable at module level (ast.parse accepts it there) and inside
        # an `async def`, where no_async reports the root cause first.
        ast.AsyncFor: "async for loops are forbidden — async has no substitute in POOP; see the async def ban",
    }
)
