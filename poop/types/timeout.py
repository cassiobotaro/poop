import asyncio
from typing import TYPE_CHECKING, Never, Self, cast, final

from poop.types import mirrors
from poop.types.boolean import to_boolean
from poop.types.error import Error
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


@final
class Timeout(Object, name="Timeout"):
    """What `Async.timeout(delay)` answers: a deadline, entered with `AsyncWith`.

    Wraps `asyncio.timeout`, which fails a body that outlasts the delay with
    `TimeoutError`. Entering answers this object, so the body holds a POOP
    value; `expired()` is the one question about it a program can act on,
    since `when` and `reschedule` speak the event loop's clock, which POOP
    does not expose.
    """

    __slots__ = ("_delay", "_raw")

    def __new__(cls, *_args: object, **_kwargs: object) -> Never:
        raise mirrors.TypeError(
            "cannot create 'Timeout' instances — send #timeout to Async"
        )

    @classmethod
    def _of(cls, delay: float | None) -> Self:
        timeout = object.__new__(cls)
        timeout._delay = delay
        timeout._raw = None
        return timeout

    def expired(self) -> Boolean:
        return to_boolean(self._raw is not None and self._raw.expired())

    async def __aenter__(self) -> Self:
        # Built here, not in `_of`: `asyncio.timeout` reads the running loop's
        # clock, and `Async.timeout(1)` is usually sent before any loop runs.
        # Entering twice keeps CPython's refusal, which a second
        # `asyncio.timeout` would not raise.
        if self._raw is not None:
            raise mirrors.RuntimeError("Timeout has already been entered")
        self._raw = asyncio.timeout(self._delay)
        await self._raw.__aenter__()
        return self

    async def __aexit__(self, kind: object, error: object, traceback: object) -> None:
        # `AsyncWith` hands an exit POOP values, and `asyncio` needs the native
        # exception back: it is how a cancellation of its own becomes the
        # `TimeoutError` it raises in its place.
        exception = error._exception if isinstance(error, Error) else None
        raw = cast("asyncio.Timeout", self._raw)
        await raw.__aexit__(
            type(exception) if exception is not None else None,
            exception,
            exception.__traceback__ if exception is not None else None,
        )
