from __future__ import annotations

import atexit as _atexit
from typing import Any, ClassVar

from poop.types.none import NoneClass, none


class Atexit:
    """Namespace mirroring Python's `atexit` module.

    `register(func, *args, **kwargs)` returns the registered callable
    so it can be used as a decorator. `unregister` removes a previous
    registration. `_run_exitfuncs` and `_clear` are exposed for
    testing — under normal use the runtime invokes them at shutdown.

    `_run_exitfuncs` only runs handlers registered through this class so
    that calling it in tests does not trigger unrelated atexit handlers
    (e.g. coverage.py's save-and-stop handler).
    """

    _handlers: ClassVar[list[tuple[Any, tuple[Any, ...], dict[str, Any]]]] = []

    @staticmethod
    def register(func: Any, *args: Any, **kwargs: Any) -> Any:
        _atexit.register(func, *args, **kwargs)
        Atexit._handlers.append((func, args, kwargs))
        return func

    @staticmethod
    def unregister(func: Any) -> NoneClass:
        _atexit.unregister(func)
        Atexit._handlers = [(f, a, k) for f, a, k in Atexit._handlers if f is not func]
        return none

    @staticmethod
    def _run_exitfuncs() -> NoneClass:
        for func, args, kwargs in reversed(Atexit._handlers):
            try:
                func(*args, **kwargs)
            except Exception:  # noqa: S110
                pass
            _atexit.unregister(func)
        Atexit._handlers.clear()
        return none

    @staticmethod
    def _clear() -> NoneClass:
        for func, _, __ in Atexit._handlers:
            _atexit.unregister(func)
        Atexit._handlers.clear()
        return none
