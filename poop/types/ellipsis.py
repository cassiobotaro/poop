from typing import final

from poop.types.object import Object


@final
class EllipsisClass(Object):
    """POOP equivalent of Python's `...`, with singleton `ellipsis`.

    Like NoneClass, it carries no behaviour of its own beyond the universal
    Object protocol: `...` is a placeholder, not a value with messages. It
    exists so `...` is not the one literal that reaches runtime as a naked
    Python primitive.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return "Ellipsis"

    __repr__ = __str__


ellipsis: EllipsisClass = EllipsisClass()

EllipsisClass.__module__ = "builtins"
EllipsisClass.__name__ = "ellipsis"
