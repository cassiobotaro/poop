from typing import TYPE_CHECKING, final

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


@final
class NoneClass(Object):
    __slots__ = ()

    def is_none(self) -> Boolean:
        from poop.types.boolean import true

        return true

    def not_none(self) -> Boolean:
        from poop.types.boolean import false

        return false

    def __str__(self) -> str:
        return "None"

    def __bool__(self) -> bool:
        return False


none: NoneClass = NoneClass()
