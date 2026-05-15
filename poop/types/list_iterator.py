from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class ListIterator(_IteratorBase, name="list_iterator"):
    __slots__ = ()
