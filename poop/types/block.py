from collections.abc import Callable
from typing import Any

from poop.types.none import NoneClass, none
from poop.types.object import Object


class Block(Object):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn

    def __call__(self, *args: Any) -> Any:
        return self._fn(*args)

    def while_true(self, body: Block) -> NoneClass:
        while bool(self._fn()):
            body()
        return none

    def while_false(self, body: Block) -> NoneClass:
        while not bool(self._fn()):
            body()
        return none

    def __str__(self) -> str:
        return f"Block({self._fn})"

    __repr__ = __str__
