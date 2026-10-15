from typing import TYPE_CHECKING, final

from poop.types._argument import a_block, no_arguments
from poop.types.boolean import false, true
from poop.types.object import _PAIR, _PAIR_SWAPPED, Object

if TYPE_CHECKING:
    from collections.abc import Callable

    from poop.types.boolean import Boolean


@final
class NoneClass(Object, name="NoneType"):
    __slots__ = ()

    # CPython's answer: `type(None)() is None`. `class_()` hands the class
    # out and a class is callable, so without this `None.class_()()` built a
    # second None — printing `None`, neither identical nor equal to the first.
    def __new__(cls, *args: object, **kwargs: object) -> NoneClass:
        no_arguments(cls, args, kwargs)
        return none

    def if_none[T](self, block: Callable[[], T]) -> T:
        return a_block(block, "if_none", param="")()

    def if_not_none(self, block: Callable[[Object], object]) -> NoneClass:
        a_block(block, "if_not_none")
        return self

    def if_none_if_not_none[T](
        self, none_block: Callable[[], T], present_block: Callable[[Object], object]
    ) -> T:
        a_block(present_block, "if_none_if_not_none", spelt=_PAIR)
        return a_block(none_block, "if_none_if_not_none", spelt=_PAIR)()

    def if_not_none_if_none[T](
        self, present_block: Callable[[Object], object], none_block: Callable[[], T]
    ) -> T:
        a_block(present_block, "if_not_none_if_none", spelt=_PAIR_SWAPPED)
        return a_block(none_block, "if_not_none_if_none", spelt=_PAIR_SWAPPED)()

    def is_none(self) -> Boolean:
        return true

    def not_none(self) -> Boolean:
        return false

    def __str__(self) -> str:
        return "None"

    def __bool__(self) -> bool:
        return False


none: NoneClass = object.__new__(NoneClass)
