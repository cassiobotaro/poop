from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class StrIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<str_iterator>"

    __repr__ = __str__
