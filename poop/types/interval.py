from builtins import all as builtins_all
from builtins import any as builtins_any
from collections import deque
from collections.abc import Callable
from functools import reduce
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass


class Interval(Object):
    __slots__ = ("_start", "_step", "_stop")

    def __init__(self, start: Int, stop: Int, step: Int | None = None) -> None:
        from poop.types.int import Int

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
        from poop.types.int import Int

        for i in self._range():
            yield Int(i)

    def do[T](self, block: Callable[[Int], T]) -> None:
        deque(map(block, self._iter()), maxlen=0)

    def map(self, block: Callable[[Int], Any]) -> List:
        from poop.types.list import List

        return List(*map(block, self._iter()))

    def filter(self, block: Callable[[Int], Any]) -> List:
        from poop.types.list import List

        return List(*[i for i in self._iter() if bool(block(i))])

    def filter_false(self, block: Callable[[Int], Any]) -> List:
        from poop.types.list import List

        return List(*[i for i in self._iter() if not bool(block(i))])

    def find(self, block: Callable[[Int], Any]) -> Int | NoneClass:
        from poop.types.none import none

        for i in self._iter():
            if bool(block(i)):
                return i
        return none

    def reduce[T](self, init: T, block: Callable[[T, Int], T]) -> T:
        return reduce(block, self._iter(), init)

    def all(self, block: Callable[[Int], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_all(bool(block(i)) for i in self._iter()) else false

    def any(self, block: Callable[[Int], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_any(bool(block(i)) for i in self._iter()) else false

    def includes(self, item: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._start._value <= item._value <= self._stop._value else false

    def count(self, value: Int) -> Int:
        from poop.types.int import Int

        return Int(self._range().count(value._value))

    def index(self, value: Int) -> Int:
        from poop.types.int import Int

        return Int(self._range().index(value._value))

    def start(self) -> Int:
        return self._start

    def stop(self) -> Int:
        return self._stop

    def step(self) -> Int:
        return self._step

    def first(self) -> Int:
        return self._start

    def last(self) -> Int:
        return self._stop

    def reversed(self) -> Interval:
        from poop.types.int import Int

        return Interval(self._stop, self._start, Int(-self._step._value))

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._range()))

    def __str__(self) -> str:
        return f"({self._start}..{self._stop})"

    __repr__ = __str__
