from collections.abc import Callable
from typing import Any, final

from poop.types.boolean import Boolean, false, true
from poop.types.object import Object


@final
class NoneClass(Object):
    __slots__ = ()

    def if_none[T](self, block: Callable[[], T]) -> T:
        return block()

    def if_not_none(self, block: Callable[[Object], Any]) -> NoneClass:
        return self

    def is_none(self) -> Boolean:
        return true

    def not_none(self) -> Boolean:
        return false

    def __str__(self) -> str:
        return "None"

    __repr__ = __str__

    def __bool__(self) -> bool:
        return False


none: NoneClass = NoneClass()
