from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.int import Int


@final
class RangeIterator(_IteratorBase[Int], name="range_iterator"):
    __slots__ = ()
