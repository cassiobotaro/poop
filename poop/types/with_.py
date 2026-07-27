from __future__ import annotations

from collections.abc import Callable
from typing import Any

from poop.types._cloak import cloak
from poop.types.exceptions import MIRRORS
from poop.types.none import none
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

    def do(self, body_block: Callable[[Any], object]) -> object:
        if self._cm_block is None:
            raise MIRRORS["RuntimeError"](
                "With has already run; create a new With instance to run again."
            )
        cm = self._cm_block()
        # Single-use: drop the context-manager block so the executed With no
        # longer pins whatever its closure captured (re-running raises).
        self._cm_block = None
        value = cm.__enter__()
        try:
            result = body_block(value)
        except BaseException as e:
            if not cm.__exit__(type(e), e, e.__traceback__):
                raise
            # __exit__ swallowed the exception, so the body never produced a
            # value to answer. Python's `with` just carries on past the block
            # here; `none` is that "carried on with nothing to show".
            return none
        else:
            cm.__exit__(None, None, None)
        return result

    def __str__(self) -> str:
        return "With"

    def __repr__(self) -> str:
        return str(self)


# Like `Try`: keep the user-facing name but drop the module, so `class_()`
# stops leaking `<class 'poop.types.with_.With'>`.
cloak(With)
