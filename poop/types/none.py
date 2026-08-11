from collections.abc import Callable
from typing import TYPE_CHECKING, Any, final

from poop.types._cloak import cloak
from poop.types.boolean import false, true
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


@final
class NoneClass(Object):
    __slots__ = ()

    def if_none[T](self, block: Callable[[], T]) -> T:
        from poop.types._argument import a_block

        return a_block(block, "if_none", param="")()

    def if_not_none(self, block: Callable[[Object], Any]) -> NoneClass:
        from poop.types._argument import a_block

        a_block(block, "if_not_none")
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

cloak(NoneClass, "NoneType")
