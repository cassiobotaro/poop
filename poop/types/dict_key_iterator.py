from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class DictKeyIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<dict_keyiterator>"

    __repr__ = __str__
