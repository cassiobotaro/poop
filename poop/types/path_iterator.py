import pathlib as _pathlib
from collections.abc import Iterable
from typing import TYPE_CHECKING, final

from poop.types._iterable_mixin import _IterableMixin
from poop.types._iterator_base import _IteratorBase

if TYPE_CHECKING:
    from poop.types.path import Path  # noqa: F401


@final
class PathIterator(_IteratorBase["Path"], _IterableMixin, name="path_iterator"):
    __slots__ = ()

    def __init__(self, source: Iterable[_pathlib.Path]) -> None:
        from poop.types.path import Path

        super().__init__(Path._from_pathlib(p) for p in source)
