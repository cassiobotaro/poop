"""Late binding for the import cycles on the paths every program runs.

`poop/types` has about 280 function-local imports, each breaking a cycle
between the hubs: `boolean` inherits from `_numeric_compare`, `block` imports
`Object`, `float` imports `int`, so none of those can name the other at module
level. The cycles are real, and a local import is the right way to break one.

It is also a cost on every call: a `from x import y` inside a function runs
`__import__` and a `sys.modules` lookup each time, about 215 ns on 3.15, where
a module global is about 20 ns. Counting the imports that fire while every
example program runs ranked the sites, and a handful carried nearly all of
them — the message dispatch in `Object.__getattribute__`, the numeric tower's
arithmetic and comparisons, `print`. Those bind late instead: `late(module,
name)` answers a getter that imports once and is a C-level `functools.cache`
hit afterwards, about 50 ns. `tests/test_hot_paths_bind_late.py` counts the
imports on those paths and expects none.

The rule for the next site: a local import for a cold path (the ~260 that
fire fewer than fifteen times across every example), `late` for one the
counter test covers. The caller annotates what it binds — `Callable[[],
type[Float]]` for a class, `Callable[[], Callable[..., Boolean]]` for a
function — with the real name imported under `TYPE_CHECKING`, so ty still
checks the call.
"""

import importlib
from functools import cache
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


def late(module: str, name: str) -> Callable[[], Any]:
    """A getter for `module.name` that imports on first call and caches."""

    @cache
    def bound() -> Any:  # noqa: ANN401 — see above
        return getattr(importlib.import_module(module), name)

    return bound
