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
