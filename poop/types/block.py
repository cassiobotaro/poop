from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


def _as_block(value: Any) -> Any:
    """A raw Python callable answered by `get_attr`, wrapped as a `Block`.

    An attribute holding state already answers a POOP object; one holding a
    *method* answered CPython's bound method, which understands no message —
    `"abc".get_attr("upper").print()` raised Python's own `AttributeError`
    instead of `does not understand #print`, the last member of the
    `getattr`-substitute family still handing back a native. `Block` is what
    every lambda is already wrapped in, so a method fetched by name reads back
    as the same kind of object a block literal does, callable included.

    A POOP class is left alone: it is callable, but it is already an object
    with its own protocol.
    """
    if callable(value) and not isinstance(value, (Object, type)):
        return Block(value)
    return value


class Block(Object):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)

    def while_true(self, body: Block) -> NoneClass:
        while bool(self._fn()):
            body()
        return none

    def while_false(self, body: Block) -> NoneClass:
        while not bool(self._fn()):
            body()
        return none

    def __str__(self) -> str:
        return "<block>"

    __repr__ = __str__


# A POOP block is a wrapped lambda, and CPython's class for a lambda is
# `function` (`type(lambda: 0).__name__`). Answer that name so `class_()` and
# `class_name()` mirror Python instead of leaking the `poop.types.block.Block`
# path — the same cloak every other wrapper applies.
cloak(Block, "function")
