from __future__ import annotations

import asyncio as _asyncio
import inspect as _inspect
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object


def _as_coro(awaitable: Any) -> Any:
    """Accept either a Python awaitable or a callable that returns one."""
    if _inspect.iscoroutine(awaitable):
        return awaitable
    if hasattr(awaitable, "__await__"):
        return awaitable
    if callable(awaitable):
        return awaitable()
    return awaitable


class Future(Object):
    """Wraps Python's `asyncio.Future`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any = None) -> None:
        self._impl = impl

    def done(self) -> Boolean:
        return true if self._impl.done() else false

    def cancelled(self) -> Boolean:
        return true if self._impl.cancelled() else false

    def result(self) -> Object:
        from poop.types._bridge import to_poop

        return to_poop(self._impl.result())

    def exception(self) -> Object:
        from poop.types._bridge import to_poop

        return to_poop(self._impl.exception())

    def cancel(self) -> Boolean:
        return true if self._impl.cancel() else false


class AsyncIO:
    """Namespace mirroring (a curated subset of) Python's `asyncio` module.

    Coroutines are written as `async def` and run via `asyncio.run`.
    The introspection-heavy parts of the asyncio API (loop policy,
    transports/protocols) are deliberately out of scope.
    """

    Future: ClassVar[type[Future]] = Future
    CancelledError: ClassVar[type[BaseException]] = _asyncio.CancelledError
    TimeoutError: ClassVar[type[BaseException]] = _asyncio.TimeoutError
    InvalidStateError: ClassVar[type[BaseException]] = _asyncio.InvalidStateError
    IncompleteReadError: ClassVar[type[BaseException]] = _asyncio.IncompleteReadError

    @staticmethod
    def run(
        main: Any, *, debug: Boolean | None = None, loop_factory: Any = None
    ) -> Any:
        d = None if debug is None else bool(debug)
        return _asyncio.run(_as_coro(main), debug=d, loop_factory=loop_factory)

    @staticmethod
    def sleep(delay: Float | Int, result: Any = None) -> Any:
        return _asyncio.sleep(delay._value, result=result)

    @staticmethod
    def gather(*coros_or_futures: Any, return_exceptions: Boolean = false) -> Any:
        return _asyncio.gather(
            *(_as_coro(a) for a in coros_or_futures),
            return_exceptions=bool(return_exceptions),
        )

    @staticmethod
    def wait_for(fut: Any, timeout: Float | Int | NoneClass | None = None) -> Any:
        from poop.types._unwrap import _opt_timeout

        return _asyncio.wait_for(_as_coro(fut), _opt_timeout(timeout))

    @staticmethod
    def shield(arg: Any) -> Any:
        return _asyncio.shield(_as_coro(arg))

    @staticmethod
    async def do(aiterable: Any, block: Any) -> NoneClass:
        """Async equivalent of `iterable.do(block)` — POOP's substitute
        for `async for`.

        Iterates an async iterable (anything implementing `__aiter__` /
        `__anext__`), calling `block` on each item. If `block` returns
        a coroutine / awaitable, it is awaited before the next iteration
        — so both sync and async bodies work.

        POOP bans `async for` syntax via the `no_loops` validator; this
        is the message-passing escape hatch. Usage (inside `async def`):

            await AsyncIO.do(stream, lambda chunk: handle(chunk))
            await AsyncIO.do(stream, lambda chunk: async_handle(chunk))
        """
        async for item in aiterable:
            result = block(item)
            if hasattr(result, "__await__"):
                await result
        return none

    @staticmethod
    def create_task(coro: Any) -> Future:
        # `create_task` requires a running loop. Surface as a Future.
        return Future(_asyncio.ensure_future(_as_coro(coro)))

    @staticmethod
    def ensure_future(coro_or_future: Any) -> Future:
        return Future(_asyncio.ensure_future(_as_coro(coro_or_future)))
