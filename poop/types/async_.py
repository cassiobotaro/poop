import asyncio
from inspect import isawaitable
from typing import TYPE_CHECKING, Never, cast, final

from poop.types import mirrors
from poop.types._bridge import to_python
from poop.types._message import describe_operand
from poop.types.coroutine import Coroutine, discard
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.timeout import Timeout

if TYPE_CHECKING:
    from collections.abc import Awaitable


def _awaitable(value: object, selector: str, expected: str) -> Awaitable[Object]:
    """`value`, or the refusal naming the message it was handed to."""
    if not isawaitable(value):
        raise mirrors.TypeError(
            f"#{selector} expects {expected}, got {describe_operand(value)}"
        )
    return value


def _loop_is_running() -> bool:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


async def _sleep(delay: float, result: object) -> object:
    return await asyncio.sleep(delay, result)


async def _gather(awaitables: tuple[Awaitable[Object], ...]) -> List:
    return List(*await asyncio.gather(*awaitables))


@final
class Async(Object, name="Async"):
    """Runs and combines coroutines: Smalltalk's `Processor`, as a class.

    Named after the keyword, as `Try` and `With` are, and holding only what
    running a coroutine needs
    (`doc/adr/0077-async-runs-coroutines-named-after-the-keyword-not-the-module.md`).
    Each message checks its arguments' kinds when it is sent, before any
    coroutine exists, so a wrong kind fails on the line that wrote it.
    """

    __slots__ = ()

    def __new__(cls, *_args: object, **_kwargs: object) -> Never:
        raise mirrors.TypeError(
            "Async has no instances — send run, sleep, gather or timeout to the class"
        )

    @staticmethod
    def run(coroutine: Awaitable[object]) -> object:
        awaitable = _awaitable(coroutine, "run", "a coroutine")
        # Inside a running loop `asyncio.run` refuses, in CPython's words,
        # before it touches its argument, and leaves that argument unawaited.
        if _loop_is_running():
            discard(awaitable)
        return asyncio.run(awaitable)

    @staticmethod
    def sleep(delay: Int | Float, result: object = none) -> Coroutine:
        if not isinstance(delay, (Int, Float)):
            raise mirrors.TypeError(
                f"#sleep expects a number, got {describe_operand(delay)}"
            )
        return Coroutine._of(_sleep(cast("float", to_python(delay)), result))

    @staticmethod
    def gather(*coroutines: Awaitable[Object]) -> Coroutine:
        try:
            awaitables = tuple(
                _awaitable(c, "gather", "coroutines") for c in coroutines
            )
        except mirrors.TypeError:
            for coroutine in coroutines:
                discard(coroutine)
            raise
        return Coroutine._of(_gather(awaitables))

    @staticmethod
    def timeout(delay: Int | Float | NoneClass) -> Timeout:
        if delay is none:
            return Timeout._of(None)
        if not isinstance(delay, (Int, Float)):
            raise mirrors.TypeError(
                f"#timeout expects a number or None, got {describe_operand(delay)}"
            )
        return Timeout._of(cast("float", to_python(delay)))
