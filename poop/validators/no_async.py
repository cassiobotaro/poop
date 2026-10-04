import ast

from poop.validators._node import NodeValidator

# `await` needs its own row: ast.parse accepts a module-level `await`
# (only compile() rejects it), so without this the node would sail past
# validation and surface as a raw CPython SyntaxError instead of a POOP
# error. `async with` / `async for` are equally reachable at module level
# but already belong to no_with and no_loops; rows here would only double
# the message.
_ASYNC_DEF = "async def is forbidden — POOP has no way to drive a coroutine"
_AWAIT = "await is forbidden — POOP has no way to drive a coroutine"


class NoAsyncValidator(NodeValidator):
    messages = {
        ast.AsyncFunctionDef: _ASYNC_DEF,
        ast.Await: _AWAIT,
    }
