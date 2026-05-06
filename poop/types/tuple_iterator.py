from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class TupleIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<tuple_iterator>"

    __repr__ = __str__
