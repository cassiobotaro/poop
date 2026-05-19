from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.int import Int


@final
class BytesIterator(_IteratorBase[Int], name="bytes_iterator"):
    __slots__ = ()
