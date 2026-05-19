from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.int import Int


@final
class ByteArrayIterator(_IteratorBase[Int], name="bytearray_iterator"):
    __slots__ = ()
