from collections import deque
from collections.abc import Callable
from functools import reduce
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.int import Int


class Interval(Object):
    def __init__(self, start: Int, stop: Int) -> None:
        self._start = start
        self._stop = stop

    def _iter(self) -> Any:
        from poop.types.int import Int

        for i in range(self._start._value, self._stop._value + 1):
            yield Int(i)

    def do[T](self, block: Callable[[Int], T]) -> None:
        deque(map(block, self._iter()), maxlen=0)

    def collect[T](self, block: Callable[[Int], T]) -> list[T]:
        return list(map(block, self._iter()))

    def select(self, block: Callable[[Int], Any]) -> list[Int]:
        return [i for i in self._iter() if bool(block(i))]

    def reject(self, block: Callable[[Int], Any]) -> list[Int]:
        return [i for i in self._iter() if not bool(block(i))]

    def detect(self, block: Callable[[Int], Any]) -> Int | None:
        for i in self._iter():
            if bool(block(i)):
                return i
        return None

    def inject_into[T](self, init: T, block: Callable[[T, Int], T]) -> T:
        return reduce(block, self._iter(), init)

    def size(self) -> Int:
        from poop.types.int import Int

        return Int(self._stop._value - self._start._value + 1)

    def __str__(self) -> str:
        return f"({self._start}..{self._stop})"
