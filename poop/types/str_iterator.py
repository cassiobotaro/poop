from typing import TYPE_CHECKING, final

from poop.types._iterator_base import _IteratorBase

if TYPE_CHECKING:
    from poop.types.string import Str  # noqa: F401


@final
class StrIterator(_IteratorBase["Str"], name="str_iterator"):
    __slots__ = ()
