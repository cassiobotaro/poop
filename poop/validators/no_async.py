import ast

from poop.validators._node import NodeValidator

# An `async def` is not refused here: whether one is legal depends on where it
# is written, which `no_free_functions` judges. `await` needs its own row
# because ast.parse accepts a module-level `await` (only compile() rejects
# it), so without this the node would surface as a raw CPython SyntaxError
# instead of a POOP error. `async with` / `async for` belong to no_with and
# no_loops; rows here would only double the message.
_AWAIT = "await is forbidden — use x.await_() instead"


class NoAsyncValidator(NodeValidator):
    messages = {ast.Await: _AWAIT}
