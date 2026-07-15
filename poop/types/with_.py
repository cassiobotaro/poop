from __future__ import annotations

from collections.abc import Callable
from typing import Any

from poop.types.object import Object


class With(Object):
    """Smalltalk-style with/as as a message-passing builder.

    Execution is deferred: the context manager block runs only when .do() is called.
    The body receives the value returned by __enter__.
    Exceptions propagate via the standard context manager protocol (__exit__).

    Trade-off: the context manager object must implement Python's __enter__/__exit__
    protocol — a deliberate primitive leak, consistent with how Try uses native
    exception types.

    Usage:
        With(lambda: open('file.txt')).do(lambda f: f.read().print())
        With(lambda: lock).do(lambda _: critical_section())
    """

    __slots__ = ("_cm_block",)

    def __init__(self, cm_block: Callable[[], Any]) -> None:
        self._cm_block: Callable[[], Any] | None = cm_block

    def do(self, body_block: Callable[[Any], object]) -> With:
        if self._cm_block is None:
            raise RuntimeError(
                "With has already run; create a new With instance to run again."
            )
        cm = self._cm_block()
        # Single-use: drop the context-manager block so the executed With no
        # longer pins whatever its closure captured (re-running raises).
        self._cm_block = None
        value = cm.__enter__()
        try:
            body_block(value)
        except BaseException as e:
            if not cm.__exit__(type(e), e, e.__traceback__):
                raise
        else:
            cm.__exit__(None, None, None)
        return self

    def __str__(self) -> str:
        return "With"

    def __repr__(self) -> str:
        return str(self)
