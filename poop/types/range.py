from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types._iterable_mixin import _IterableMixin
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
        stop: Int | None = None,
        step: Int | None = None,
    ) -> List:
        from poop.types.slice import Slice

        items = list(self._iter())
        if isinstance(start_or_slice, Slice):
            return List(*items[start_or_slice._py_slice()])
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return List(*items[start_or_slice._value : stop._value : s])

    def includes(self, item: Int) -> Boolean:
        return to_boolean(item._value in self._range())

    def count(self, value: Int) -> Int:
        return Int(self._range().count(value._value))

    def index(self, value: Int) -> Int:
        return Int(self._range().index(value._value))

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
        return Int(self._range()[index._value])

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

    def __str__(self) -> str:
        start, stop = self._start._value, self._stop._value
        step = self._step._value
        if step == 1:
            return f"range({start}, {stop})"
        return f"range({start}, {stop}, {step})"

    __repr__ = __str__


Range.__module__ = "builtins"
Range.__name__ = "range"
