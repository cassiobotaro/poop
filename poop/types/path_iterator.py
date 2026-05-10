import pathlib as _pathlib
from collections.abc import Iterable
from typing import final

from poop.types._iterable_mixin import _IterableMixin
from poop.types._iterator_base import _IteratorBase


@final
class PathIterator(_IteratorBase, _IterableMixin):
    __slots__ = ()

    def __init__(self, source: Iterable[_pathlib.Path]) -> None:
        from poop.types.path import Path

        super().__init__(Path._from_pathlib(p) for p in source)

    def __str__(self) -> str:
        return "<path_iterator>"

    __repr__ = __str__
