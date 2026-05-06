from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class MemoryViewIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<memory_iterator>"

    __repr__ = __str__
