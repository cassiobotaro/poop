from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class BytesIterator(_IteratorBase, name="bytes_iterator"):
    __slots__ = ()
