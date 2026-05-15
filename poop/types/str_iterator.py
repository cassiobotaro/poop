from typing import final

from poop.types._iterator_base import _IteratorBase


@final
class StrIterator(_IteratorBase, name="str_iterator"):
    __slots__ = ()
