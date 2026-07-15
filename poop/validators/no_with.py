import ast

from poop.validators._node import make_node_validator

NoWithValidator = make_node_validator(
    {
        ast.With: "with is forbidden — use With(lambda: cm()).do(lambda resource: body) instead",
        # Reachable at module level (ast.parse accepts it there) and inside
        # an `async def`, where no_async reports the root cause first.
        ast.AsyncWith: "async with is forbidden — async has no substitute in POOP; see the async def ban",
    }
)
