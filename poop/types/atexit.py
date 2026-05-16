from __future__ import annotations

import atexit as _atexit
from typing import Any

from poop.types.none import NoneClass, none


class Atexit:
    """Namespace mirroring Python's `atexit` module.

    `register(func, *args, **kwargs)` returns the registered callable
    so it can be used as a decorator. `unregister` removes a previous
    registration. `_run_exitfuncs` and `_clear` are exposed for
    testing — under normal use the runtime invokes them at shutdown.
    """

    @staticmethod
    def register(func: Any, *args: Any, **kwargs: Any) -> Any:
        return _atexit.register(func, *args, **kwargs)

    @staticmethod
    def unregister(func: Any) -> NoneClass:
        _atexit.unregister(func)
        return none

    @staticmethod
    def _run_exitfuncs() -> NoneClass:
        _atexit._run_exitfuncs()
        return none

    @staticmethod
    def _clear() -> NoneClass:
        _atexit._clear()
        return none
