import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._peek import _UNPEEKED, _PeekMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.exceptions import MIRRORS
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass


def _ran_out(position: int) -> Exception:
    """The mirrored refusal for a collection that ended before the first one."""
    return MIRRORS["ValueError"](
        f"zip is strict: collection {position + 1} ran out while "
        "collection 1 still had elements"
    )


def _refuse_leftovers(iterators: list[Iterator[Any]]) -> None:
    """Refuse if any collection outlasts the first, which has just ended."""
    for position, iterator in enumerate(iterators[1:], 1):
        try:
            next(iterator)
        except StopIteration:
            continue
        raise MIRRORS["ValueError"](
            f"zip is strict: collection {position + 1} still had elements "
            "when collection 1 ran out"
        )


class Zip(_PeekMixin, _IterableMixin, Object):
    __slots__ = ("_iter", "_sources", "_strict")

    def __init__(
        self, *sources: Any, strict: Boolean | NoneClass | None = None
    ) -> None:
        from poop.types._unwrap import _unwrap_bool

        for source in sources:
            iter(source)
        self._sources = sources
        self._strict: Boolean = to_boolean(_unwrap_bool(strict, False))
        self._iter: Iterator[Tuple] | None = None
        self._peeked: Any = _UNPEEKED

    @staticmethod
    def _gen(sources: tuple[Any, ...], strict: bool) -> Iterator[Tuple]:
        """The lazy pairing, with the strict mismatch worded as POOP.

        CPython answers `zip() argument 2 is shorter than argument 1` — the
        builtin spelled as the call `a.zip(b)` substitutes, and arguments
        numbered from that call's perspective, where the receiver is argument
        1 and the first argument the program passed is argument 2. POOP drives
        the sources itself when `strict` is asked for, so the position in the
        sentence is the position among the collections being zipped, which is
        the same number in both spellings (`a.zip(b)` and `zip(a, b)`).
        """
        if not strict:
            for items in _builtins.zip(*sources):
                yield Tuple(*items)
            return
        iterators = [iter(source) for source in sources]
        if not iterators:
            # `zip()` over nothing pairs nothing — and an empty round below
            # would yield an empty Tuple forever.
            return
        while True:
            items = []
            for position, iterator in enumerate(iterators):
                try:
                    items.append(next(iterator))
                except StopIteration:
                    if position:
                        raise _ran_out(position) from None
                    _refuse_leftovers(iterators)
                    return
            yield Tuple(*items)

    def _materialize(self) -> Iterator[Tuple]:
        if self._iter is None:
            self._iter = self._gen(self._sources, bool(self._strict))
            # The generator now owns the sources; drop our copy so a consumed
            # Zip stops pinning all of its source iterables.
            self._sources = ()
        return self._iter

    def __iter__(self) -> Iterator[Tuple]:
        # `self`, not the raw generator: an element parked by `has_next` would
        # otherwise be skipped by whatever iterated next.
        return self

    def iter(self) -> Zip:
        return self

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:

        return false if self is other else true

    def __str__(self) -> str:
        return "<zip>"

    __repr__ = __str__


cloak(Zip, "zip")
