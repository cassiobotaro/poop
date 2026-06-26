from __future__ import annotations

from collections.abc import Callable

from poop.types.error import Error
from poop.types.object import Object


class Try(Object):
    """Smalltalk-style try/except/finally as a message-passing builder.

    Execution is deferred: the block runs only when .run() or .finally_() is called.
    Unhandled exceptions are always re-raised.

    Usage:
        Try(lambda: risky()).except_(ValueError, lambda e: e.message().print()).run()
        Try(lambda: risky()).except_(ValueError, handler).finally_(lambda: cleanup())
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
        self._handlers.append((exc_type, handler))
        return self

    def finally_(self, block: Callable[[], object] | None = None) -> Try:
        self._finally_block = block
        return self._execute()

    def run(self) -> Try:
        return self._execute()

    def _execute(self) -> Try:
        if self._executed:
            raise RuntimeError(
                "Try has already been executed; create a new Try instance to retry."
            )
        self._executed = True
        block = self._block
        try:
            if block is not None:
                block()
        except BaseException as e:
            for exc_type, handler in self._handlers:
                if isinstance(e, exc_type):
                    handler(Error(e))
                    break
            else:
                raise
        finally:
            if self._finally_block is not None:
                self._finally_block()
            # Single-use: drop the block/handler closures so the executed
            # Try no longer pins whatever they captured (re-running raises).
            self._block = None
            self._handlers = []
            self._finally_block = None
        return self

    def __str__(self) -> str:
        return "Try"

    def __repr__(self) -> str:
        return str(self)
