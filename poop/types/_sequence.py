"""What `List` and `Tuple` answer alike.

The two classes spelled thirteen members identically except for the
constructor name. The dunders live here outright and build their results
through `_rewrap`, the hook `_BytesLikeMixin` and `_SetAlgebraMixin` use for
the same reason: the builtin answers its own kind from a method sent to a
subclass.

The *messages* do not move. A wrong-arity call is reported under the
function's `__qualname__`, and one function cannot read both `list.index()`
and `tuple.index()` — so each class keeps a one-line `def` naming itself, and
the bodies worth sharing (`index`, `print`) live here as private helpers.
"""

import builtins
from typing import TYPE_CHECKING, Self

from poop.types._argument import _opt_stop, a_bound
from poop.types._at import no_element_equal_to
from poop.types._cloak import cloak
from poop.types._repeat import _repeat_count
from poop.types._sentinel import NOT_A_COUNT
from poop.types._unwrap import _unwrap, _unwrap_bool
from poop.types.int import Int
from poop.types.none import none

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass
    from poop.types.object import Object
    from poop.types.string import Str


class _SequenceMixin:
    # An empty `__slots__`, because a slot-less class anywhere in an MRO
    # restores the per-instance `__dict__` for everything below it — see the
    # note in `_value_eq.py`.
    __slots__ = ()

    # The two payloads the mixin reads `len`, `iter`, `in`, `*` and `index`
    # off. Not `Sequence[Object]`: the ABC declares no `*`, and repeating is
    # one of the five things done here. Each concrete class narrows its own.
    _items: list[Object] | tuple[Object, ...]

    def _rewrap(self, raw: Iterable[Object]) -> Self:
        """`raw`'s elements as the receiver's own builtin kind."""
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __mul__(self, other: object) -> Self:
        count = _repeat_count(other)
        if count is NOT_A_COUNT:
            return NotImplemented
        return self._rewrap(self._items * count)

    __rmul__ = __mul__

    def _index_of(
        self,
        obj: Object,
        start: Int | NoneClass | None,
        stop: Index | NoneClass | None,
    ) -> Int:
        # No branching on which bound was given: `stop` alone was dropped on
        # the floor by the first branch, so `xs.index(3, stop=1)` answered a
        # match from outside the bound it was handed. `len` rather than `None`
        # for the missing `stop`, because `list.index` — unlike `str.index` —
        # takes no `None` bound.
        try:
            return Int(
                self._items.index(
                    obj,
                    a_bound(start, "index", "start") or 0,
                    _opt_stop(a_bound(stop, "index", "stop"), len(self._items)),
                )
            )
        except ValueError:
            raise no_element_equal_to(self, obj) from None

    def _print_items(
        self,
        sep: Str | NoneClass | None,
        end: Str | NoneClass | None,
        flush: Boolean | NoneClass | None,
    ) -> NoneClass:
        builtins.print(  # noqa: T201 — the language's own #print
            *[str(item) for item in self._items],
            sep=_unwrap(sep, " "),
            end=_unwrap(end, "\n"),
            flush=_unwrap_bool(flush, False),
        )
        return none


cloak(_SequenceMixin, "object")
