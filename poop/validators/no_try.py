import ast

from poop.validators._node import NodeValidator


class NoTryValidator(NodeValidator):
    messages = {
        ast.Try: "try/except is forbidden — use Try(block).except_(ExcType, handler).run() instead",
        # A definitive ban: exception groups come from asyncio's TaskGroup and
        # from concurrency, none of which POOP has, so no `Try` spelling could
        # be the substitute this used to name.
        ast.TryStar: "try/except* is forbidden — nothing in POOP raises an exception group",
    }
