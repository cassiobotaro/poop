from __future__ import annotations

from collections.abc import Callable

from poop.types.error import Error
from poop.types.none import none
from poop.types.object import Object


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
        self._block: Callable[[], object] | None = block
        self._handlers: list[tuple[type[BaseException], Callable[[Error], object]]] = []
        self._finally_block: Callable[[], object] | None = None
        self._executed = False

    def except_(
        self,
        exc_type: type[BaseException],
        handler: Callable[[Error], object],
    ) -> Try:
        # Once executed the single-use drop has already run; re-populating
        # _handlers would pin the handler closure (and whatever it captured)
        # on a Try that can never consume it again.
        if not self._executed:
            self._handlers.append((exc_type, handler))
        return self

    def finally_(self, block: Callable[[], object] | None = None) -> object:
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
            raise RuntimeError(
                "Try has already been executed; create a new Try instance to retry."
            )
        self._executed = True
        block = self._block
        result: object = none
        try:
            if block is not None:
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
Try.__module__ = "builtins"
