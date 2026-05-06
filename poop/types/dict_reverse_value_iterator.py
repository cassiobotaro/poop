from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class DictReverseValueIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<dict_reversevalueiterator>"

    __repr__ = __str__
