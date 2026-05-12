from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.range_iterator import RangeIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.slice import Slice


class Range(_IterableMixin, Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(self, start: Int, stop: Int, step: Int | None = None) -> None:
        if step is not None and step._value == 0:
            raise ValueError("step must not be zero")
        self._start = start
        self._stop = stop
        self._step = (
            step if step is not None else Int(1 if start._value <= stop._value else -1)
        )

    def _range(self) -> range:
        start, stop, step = self._start._value, self._stop._value, self._step._value
        sign = 1 if step > 0 else -1
        return range(start, stop + sign, step)

    def _iter(self) -> Any:
        for i in self._range():
            yield Int(i)

    def __iter__(self) -> Any:
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
            s = (
                start_or_slice._step._value
                if start_or_slice._step is not None
                else None
            )
            return List(
                *items[start_or_slice._start._value : start_or_slice._stop._value : s]
            )
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return List(*items[start_or_slice._value : stop._value : s])

    def includes(self, item: Int) -> Boolean:
        return true if item._value in self._range() else false

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
        return Range(self._stop, self._start, Int(-self._step._value))

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
