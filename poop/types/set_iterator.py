from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class SetIterator(_IteratorBase):
    __slots__ = ()

    def __str__(self) -> str:
        return "<set_iterator>"

    __repr__ = __str__
