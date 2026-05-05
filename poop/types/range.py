from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Range(_IterableMixin, Object):
    __slots__ = ("_start", "_step", "_stop")

    def __init__(self, start: Int, stop: Int, step: Int | None = None) -> None:
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

    def slice(self, start: Int, stop: Int, step: Int | None = None) -> List:
        s = step._value if step is not None else None
        items = list(self._iter())
        return List(*items[start._value : stop._value : s])

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

    def first(self) -> Int:
        return self._start

    def last(self) -> Int:
        return self._stop

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
