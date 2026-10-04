from collections.abc import Callable
from typing import TYPE_CHECKING, Any, final

from poop.types._argument import a_block, no_arguments
from poop.types._cloak import cloak
from poop.types.boolean import false, true
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


@final
class NoneClass(Object):
    __slots__ = ()

    # CPython's answer: `type(None)() is None`. `class_()` hands the class
    # out and a class is callable, so without this `None.class_()()` built a
    # second None — printing `None`, neither identical nor equal to the first.
    def __new__(cls, *args: object, **kwargs: object) -> NoneClass:
        no_arguments(cls, args, kwargs)
        return none

    def if_none[T](self, block: Callable[[], T]) -> T:
        return a_block(block, "if_none", param="")()

    def if_not_none(self, block: Callable[[Object], Any]) -> NoneClass:
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


none: NoneClass = object.__new__(NoneClass)

cloak(NoneClass, "NoneType")
