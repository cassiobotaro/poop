from typing import final

from poop.types._argument import no_arguments
from poop.types._cloak import cloak
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

    # `type(...)() is ...` in CPython; see `NoneClass.__new__`.
    def __new__(cls, *args: object, **kwargs: object) -> EllipsisClass:
        no_arguments(cls, args, kwargs)
        return ellipsis

    def __str__(self) -> str:
        return "Ellipsis"

    __repr__ = __str__


ellipsis: EllipsisClass = object.__new__(EllipsisClass)

cloak(EllipsisClass, "ellipsis")
