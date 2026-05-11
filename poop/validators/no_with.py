import ast

from poop.validators._node import make_node_validator

NoWithValidator = make_node_validator(
    {
        ast.With: "with is forbidden — use With(lambda: cm()).do(lambda resource: body) instead",
        ast.AsyncWith: "async with is forbidden — use With(lambda: cm()).do(lambda resource: body) instead",
    }
)
