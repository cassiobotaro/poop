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


class AsyncWith(Object):
    """Async-context-manager equivalent of `With`.

    POOP bans `async with` syntax via the `no_with` validator; this is
    the message-passing substitute. The body block runs inside the
    async context; if it returns a coroutine/awaitable, `AsyncWith.do`
    awaits it before exiting the manager.

    The context-manager block must produce an object that implements
    `__aenter__` / `__aexit__` (Python's async context-manager
    protocol) — a deliberate primitive leak, same trade-off as `With`.

    Usage (inside an `async def`):
        await AsyncWith(lambda: aiohttp_session()).do(
            lambda session: handle(session)
        )
    """

    __slots__ = ("_acm_block",)

    def __init__(self, acm_block: Callable[[], Any]) -> None:
        self._acm_block: Callable[[], Any] | None = acm_block

    async def do(self, body_block: Callable[[Any], object]) -> AsyncWith:
        if self._acm_block is None:
            raise RuntimeError(
                "AsyncWith has already run; create a new AsyncWith instance "
                "to run again."
            )
        acm = self._acm_block()
        # Single-use: drop the context-manager block so the executed AsyncWith
        # no longer pins whatever its closure captured (re-running raises).
        self._acm_block = None
        value = await acm.__aenter__()
        try:
            result = body_block(value)
            if hasattr(result, "__await__"):
                await result  # ty: ignore[invalid-await]
        except BaseException as e:
            suppress = await acm.__aexit__(type(e), e, e.__traceback__)
            if not suppress:
                raise
        else:
            await acm.__aexit__(None, None, None)
        return self

    def __str__(self) -> str:
        return "AsyncWith"

    def __repr__(self) -> str:
        return str(self)
