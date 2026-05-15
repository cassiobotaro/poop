from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class TupleIterator(_IteratorBase, name="tuple_iterator"):
    __slots__ = ()
