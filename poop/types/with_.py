from __future__ import annotations

from collections.abc import Callable
from typing import Any

from poop.types._cloak import cloak
from poop.types.block import _require_block
from poop.types.exceptions import MIRRORS
from poop.types.none import none
from poop.types.object import Object


def _protocol(cm: Any) -> tuple[Any, Any]:
    """`cm`'s `__enter__` / `__exit__`, or CPython's own refusal.

    Both slots are resolved before either is called, as Python's `with` does.
    Entering first and reaching for `__exit__` only afterwards ran the
    acquisition of a manager that can never release it — the entry side effect
    happened, and nothing was ever going to undo it.

    Looked up on the type, not the instance: that is where Python's protocol
    reads them from, so a `does_not_understand` hook cannot forge a context
    manager. CPython names the missing dunder here; POOP says which half of
    the protocol is missing instead, since a diagnostic that spells
    `__exit__` names the very construct `no_dunder_attribute` bans.
    """
    for slot, verb in (("__enter__", "entered"), ("__exit__", "exited")):
        if not hasattr(type(cm), slot):
            raise MIRRORS["TypeError"](
                f"{type(cm).__name__} does not support the context manager "
                f"protocol — it cannot be {verb}"
            )
    return type(cm).__enter__, type(cm).__exit__


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
        self._cm_block: Callable[[], Any] | None = _require_block(
            cm_block, "the manager argument", "write With(lambda: …)"
        )

    def do(self, body_block: Callable[[Any], object]) -> object:
        if self._cm_block is None:
            raise MIRRORS["RuntimeError"](
                "With has already run; create a new With instance to run again."
            )
        cm = self._cm_block()
        # Single-use: drop the context-manager block so the executed With no
        # longer pins whatever its closure captured (re-running raises).
        self._cm_block = None
        enter, exit_ = _protocol(cm)
        value = enter(cm)
        try:
            result = body_block(value)
        except BaseException as e:
            if not exit_(cm, type(e), e, e.__traceback__):
                raise
            # __exit__ swallowed the exception, so the body never produced a
            # value to answer. Python's `with` just carries on past the block
            # here; `none` is that "carried on with nothing to show".
            return none
        else:
            exit_(cm, None, None, None)
        return result

    def __str__(self) -> str:
        return "With"

    def __repr__(self) -> str:
        return str(self)


# Like `Try`: keep the user-facing name but drop the module, so `class_()`
# stops leaking `<class 'poop.types.with_.With'>`.
cloak(With)
