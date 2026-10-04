import builtins
from typing import TYPE_CHECKING, Any

from poop.types._argument import a_collection
from poop.types._iterator_base import _LazyView
from poop.types._unwrap import _unwrap_bool
from poop.types.boolean import to_boolean
from poop.types.exceptions import MIRRORS
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.boolean import Boolean
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


class Zip(_LazyView[Tuple], name="zip"):
    __slots__ = ("_sources", "_strict")

    def __init__(
        self, *sources: Any, strict: Boolean | NoneClass | None = None
    ) -> None:
        super().__init__()
        for source in sources:
            a_collection(source, "zip")
        self._sources = sources
        self._strict: Boolean = to_boolean(_unwrap_bool(strict, False))

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
            # Shortest wins, as CPython's own non-strict `zip` does.
            for items in builtins.zip(*sources, strict=False):
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

    def _generate(self) -> Iterator[Tuple]:
        sources = self._sources
        self._sources = ()
        return self._gen(sources, bool(self._strict))
