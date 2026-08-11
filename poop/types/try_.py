from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from poop.types._argument import a_class
from poop.types._cloak import cloak
from poop.types.block import _require_block
from poop.types.error import Error
from poop.types.exceptions import MIRRORS
from poop.types.none import none
from poop.types.object import Object
from poop.types.tuple import Tuple


def _exception_kind(kind: object) -> Any:
    """The kind `except_` will match on, checked where it was written.

    `except_` guarded its handler at the boundary and left the kind to
    `isinstance` inside `_execute`, so a quoted class name answered
    `isinstance() arg 2 must be a type, a tuple of types, or a union` — the
    banned builtin spelt as the call replacing it, which proposal 10 closed on
    all 15 receivers — and answered it only when the protected block *raised*.
    The same mistake reported or said nothing depending on something else
    entirely, and saying nothing means the handler was never installed.

    A POOP `Tuple` unwraps to the native one `isinstance` needs, so Python's
    own "catch either" spelling works rather than merely failing better; and a
    class that is no exception is refused, as CPython refuses `except int`,
    because a handler that can never fire is a mistake worth naming.
    """
    resolved = a_class(
        tuple(kind._items) if isinstance(kind, Tuple) else kind, "except_"
    )
    members = resolved if isinstance(resolved, tuple) else (resolved,)
    for member in members:
        if not (isinstance(member, type) and issubclass(member, BaseException)):
            raise MIRRORS["TypeError"](
                f"#except_ catches exception classes, and "
                f"{getattr(member, '__name__', member)!s} is not one"
            )
    return resolved


class Try(Object):
    """Smalltalk-style try/except/finally as a message-passing builder.

    Execution is deferred: the block runs only when .run() or .finally_() is called.
    Unhandled exceptions are always re-raised.

    `.run()` and `.finally_()` answer the protected block's value, or the
    matching handler's when one fires — like every other POOP block, and like
    Smalltalk's `on:do:`. Both are terminal; `.except_()` is what chains.

    Usage:
        Try(lambda: risky()).except_(ValueError, lambda e: e.message().print()).run()
        Try(lambda: risky()).except_(ValueError, handler).finally_(lambda: cleanup())
        value = Try(lambda: int(text)).except_(ValueError, lambda e: -1).run()
    """

    __slots__ = ("_block", "_executed", "_finally_block", "_handlers")

    def __init__(self, block: Callable[[], object]) -> None:
        self._block: Callable[[], object] | None = _require_block(
            block, "the protected argument", "write Try(lambda: …)"
        )
        self._handlers: list[tuple[type[BaseException], Callable[[Error], object]]] = []
        self._finally_block: Callable[[], object] | None = None
        self._executed = False

    def except_(
        self,
        exc_type: type[BaseException],
        handler: Callable[[Error], object],
    ) -> Try:
        # Both arguments checked here, where each has a name — the kind used to
        # be stored untouched and first looked at by `isinstance`, inside
        # `_execute`. See `_exception_kind`.
        kind = _exception_kind(exc_type)
        _require_block(
            handler, "the handler", "write .except_(ValueError, lambda e: …)"
        )
        # Once executed the single-use drop has already run; re-populating
        # _handlers would pin the handler closure (and whatever it captured)
        # on a Try that can never consume it again.
        if not self._executed:
            self._handlers.append((kind, handler))
        return self

    def finally_(self, block: Callable[[], object] | None = None) -> object:
        # The one block argument on `Try` that was not routed through
        # `_require_block`: `.finally_(5)` reached the deferred call and
        # answered `'int' object is not callable`, while `.except_(E, 5)` — one
        # method up, in the same class — named the handler.
        if block is not None:
            _require_block(block, "the cleanup", "write .finally_(lambda: …)")
        # Store the cleanup closure only while the Try can still run it; a
        # post-execution call is rejected by _execute() below, so retaining
        # `block` here would leak it on the already-dead Try.
        if not self._executed:
            self._finally_block = block
        return self._execute()

    def run(self) -> object:
        return self._execute()

    def _execute(self) -> object:
        if self._executed:
            raise MIRRORS["RuntimeError"](
                "Try has already been executed; create a new Try instance to retry."
            )
        self._executed = True
        # `_block` is never None here: `__init__` refuses a non-callable, and
        # the post-run drop below is unreachable behind the guard above.
        block = cast("Callable[[], object]", self._block)
        result: object = none
        try:
            result = block()
        except BaseException as e:
            for exc_type, handler in self._handlers:
                if isinstance(e, exc_type):
                    result = handler(Error(e))
                    break
            else:
                raise
        finally:
            # The cleanup block's own value is discarded, mirroring
            # Smalltalk's `ensure:` — it answers the protected block's value.
            if self._finally_block is not None:
                self._finally_block()
            # Single-use: drop the block/handler closures so the executed
            # Try no longer pins whatever they captured (re-running raises).
            self._block = None
            self._handlers = []
            self._finally_block = None
        return result

    def __str__(self) -> str:
        return "Try"

    def __repr__(self) -> str:
        return str(self)


# `Try` is a legitimate user-facing name, but without this cloak `class_()`
# answers `<class 'poop.types.try_.Try'>`, leaking the internal path. Keep the
# name, drop the module, matching every other wrapper.
cloak(Try)
