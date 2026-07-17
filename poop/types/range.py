from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _faithful
from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.range_iterator import RangeIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice


class Range(_IterableMixin, Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(
        self,
        start: Int,
        stop: Int,
        step: Int | NoneClass | None = None,
    ) -> None:
        from poop.types._unwrap import _is_absent

        resolved: Int
        if _is_absent(step):
            resolved = Int(1 if start._value <= stop._value else -1)
        else:
            resolved = step
        if resolved._value == 0:
            raise ValueError("step must not be zero")
        self._start = start
        self._stop = stop
        self._step: Int = resolved

    def _range(self) -> range:
        start, stop, step = self._start._value, self._stop._value, self._step._value
        sign = 1 if step > 0 else -1
        return range(start, stop + sign, step)

    def _iter(self) -> Iterator[Int]:
        for i in self._range():
            yield Int(i)

    def __iter__(self) -> Iterator[Int]:
        return self._iter()

    def iter(self) -> RangeIterator:
        return RangeIterator(self)

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> List:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            py = start_or_slice._py_slice()
        else:
            py = Slice(start_or_slice, stop, step)._py_slice()
        # Slice the native range lazily (O(1)) and wrap only the selected
        # elements — materializing the whole range as Int objects first would
        # allocate every member just to discard all but the slice.
        return List(*(Int(i) for i in self._range()[py]))

    def includes(self, item: Int) -> Boolean:
        # getattr-unwrap: a non-`_value` argument (List, Set, …) reaches
        # range.__contains__ raw, which answers False by equality scan (as in
        # Python), instead of leaking the internal `_value` name through dispatch.
        return to_boolean(_faithful(item) in self._range())

    def count(self, value: Int) -> Int:
        return Int(self._range().count(_faithful(value)))

    def index(self, value: Int) -> Int:
        return Int(self._range().index(_faithful(value)))

    @property
    def start(self) -> Int:
        return self._start

    @property
    def stop(self) -> Int:
        return self._stop

    @property
    def step(self) -> Int:
        return self._step

    def at(self, index: Int) -> Int:
        return Int(self._range()[_faithful(index)])

    def reversed(self) -> Range:
        # Reverse the materialized forward sequence and re-encode it as a
        # POOP Range. POOP ranges use an inclusive upper bound (`_range`
        # adds `sign` to stop), so the forward sequence's last element is
        # not necessarily `_stop`: Range(0, 10, 3) yields [0, 3, 6, 9], so
        # seeding the reversed range from `_stop` (10) would produce the
        # non-members [10, 7, 4, 1]. Slice-reverse gives the correct,
        # empty-safe sequence; shift the resulting exclusive stop back by
        # `sign` to round-trip through __init__'s inclusive convention.
        reversed_range = self._range()[::-1]
        sign = 1 if reversed_range.step > 0 else -1
        return Range(
            Int(reversed_range.start),
            Int(reversed_range.stop - sign),
            Int(reversed_range.step),
        )

    def len(self) -> Int:
        return Int(len(self._range()))

    def __eq__(self, other: object) -> Boolean:
        # Mirror Python's `range` value equality: two ranges are equal when
        # they produce the same sequence. POOP's inclusive upper bound is an
        # internal encoding, so compare the materialized native ranges rather
        # than the raw `_start`/`_stop`/`_step` fields (e.g. Range(0, 4, 2)
        # and Range(0, 5, 2) both yield [0, 2, 4] and must compare equal).
        if isinstance(other, Range):
            return to_boolean(self._range() == other._range())
        return to_boolean(False)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if bool(self == other) else true

    def __hash__(self) -> int:
        # Equal ranges must hash equally; defer to the native range's hash,
        # which is consistent with its value-equality semantics.
        return hash(self._range())

    def __str__(self) -> str:
        start, stop = self._start._value, self._stop._value
        step = self._step._value
        if step == 1:
            return f"range({start}, {stop})"
        return f"range({start}, {stop}, {step})"

    __repr__ = __str__


Range.__module__ = "builtins"
Range.__name__ = "range"
