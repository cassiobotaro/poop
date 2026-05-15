from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class ByteArrayIterator(_IteratorBase, name="bytearray_iterator"):
    __slots__ = ()
