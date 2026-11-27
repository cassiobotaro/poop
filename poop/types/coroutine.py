from inspect import isawaitable
from typing import TYPE_CHECKING, Never, Self, final

from poop.types import mirrors
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Coroutine as _Raw
    from collections.abc import Generator


@final
class Coroutine(Object, name="coroutine"):
    """What an async method answers: its body, not yet run.

    Holds CPython's coroutine and offers only `__await__` from its protocol,
    so `asyncio` and `await` accept it while `cr_frame`, `send` and `throw`
    stay out of reach and an unknown message reaches `does_not_understand`
    (`doc/adr/0076-an-async-method-answers-a-coroutine-wrapped-where-the-class-is-built.md`).
    """

    __slots__ = ("_raw",)

    def __new__(cls, *_args: object, **_kwargs: object) -> Never:
        # CPython's own refusal for `type(coro)()`: only an async method makes
        # one, through `_of`.
        raise mirrors.TypeError("cannot create 'coroutine' instances")

    @classmethod
    def _of(cls, raw: _Raw[object, object, object]) -> Self:
        coroutine = object.__new__(cls)
        coroutine._raw = raw
        return coroutine

    def __await__(self) -> Generator[object, None, object]:
        return self._raw.__await__()


def discard(value: object) -> None:
    """Close `value` when it is a `Coroutine` a refused send was handed, so
    the refusal is not followed by a warning that it was never awaited.

    Any other value is left alone: an awaitable that is not a `Coroutine`,
    such as an unexecuted `Try`, holds no coroutine yet.
    """
    if isinstance(value, Coroutine):
        value._raw.close()


def refuse_awaitable(value: object, owner: str, sentence: str) -> None:
    """Refuse `value` with `sentence` when it can be awaited, after
    discarding it.

    For the synchronous forms, `Try.run` and `With.do`, whose guard would be
    over before the coroutine ran. `owner` names the block for the other
    awaitable a program can hold, a `Try` that has not run, which is not a
    coroutine and is most often a forgotten `run`.
    """
    if not isawaitable(value):
        return
    if not isinstance(value, Coroutine):
        raise mirrors.TypeError(
            f"{owner} answered a Try that has not run — send #run to it"
        )
    discard(value)
    raise mirrors.TypeError(sentence)
