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
    from poop.types.none import NoneClass


class Interval(Object):
    __slots__ = ("_start", "_stop")

    def __init__(self, start: Int, stop: Int) -> None:
        self._start = start
        self._stop = stop

    def _iter(self) -> Any:
        from poop.types.int import Int

        start, stop = self._start._value, self._stop._value
        step = 1 if start <= stop else -1
        for i in range(start, stop + step, step):
            yield Int(i)

    def do[T](self, block: Callable[[Int], T]) -> None:
        deque(map(block, self._iter()), maxlen=0)

    def collect[T](self, block: Callable[[Int], T]) -> list[T]:
        return list(map(block, self._iter()))

    def select(self, block: Callable[[Int], Any]) -> list[Int]:
        return [i for i in self._iter() if bool(block(i))]

    def reject(self, block: Callable[[Int], Any]) -> list[Int]:
        return [i for i in self._iter() if not bool(block(i))]

    def detect(self, block: Callable[[Int], Any]) -> Int | NoneClass:
        from poop.types.none import none

        for i in self._iter():
            if bool(block(i)):
                return i
        return none

    def inject_into[T](self, init: T, block: Callable[[T, Int], T]) -> T:
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

    def first(self) -> Int:
        return self._start

    def last(self) -> Int:
        return self._stop

    def reversed(self) -> Interval:
        return Interval(self._stop, self._start)

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(abs(self._stop._value - self._start._value) + 1)

    def __str__(self) -> str:
        return f"({self._start}..{self._stop})"
