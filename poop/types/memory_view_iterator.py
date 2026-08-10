from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.int import Int


@final
class MemoryViewIterator(
    _IteratorBase[Int], name="memory_iterator", iterating="memoryview"
):
    __slots__ = ()
