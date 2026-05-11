import ast

from poop.validators._node import make_node_validator

NoTryValidator = make_node_validator(
    {
        ast.Try: "try/except is forbidden — use Try(block).except_(ExcType, handler).run() instead",
        ast.TryStar: "try/except* is forbidden — use Try(block).except_(ExcType, handler).run() instead",
    }
)
