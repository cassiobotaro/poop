import ast

from poop.validators._node import NodeValidator


class NoTryValidator(NodeValidator):
    messages = {
        ast.Try: "try/except is forbidden — use Try(block).except_(ExcType, handler).run() instead",
        ast.TryStar: "try/except* is forbidden — use Try(block).except_(ExcType, handler).run() instead",
    }
