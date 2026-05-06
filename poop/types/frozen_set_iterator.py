from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class FrozenSetIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<frozenset_iterator>"

    __repr__ = __str__
