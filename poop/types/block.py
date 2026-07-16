from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


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
Block.__module__ = "builtins"
Block.__name__ = "function"
