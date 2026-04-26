from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass


class Range(_IterableMixin, Object):
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

    def __iter__(self) -> Any:
        return self._iter()

    def _iter_items(self) -> Any:
        return self._iter()

    def _collect(self, items: Any) -> Any:
        from poop.types.list import List

        return List(*items)

    def copy_from_to(self, start: Int, stop: Int, step: Int | None = None) -> List:
        from poop.types.list import List

        s = step._value if step is not None else None
        items = list(self._iter())
        return List(*items[start._value : stop._value : s])

    def includes(self, item: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if item._value in self._range() else false

    def count(self, value: Int) -> Int:
        from poop.types.int import Int

        return Int(self._range().count(value._value))

    def index(self, value: Int) -> Int:
        from poop.types.int import Int

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
        from poop.types.int import Int

        return Range(self._stop, self._start, Int(-self._step._value))

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._range()))

    def __str__(self) -> str:
        return repr(self._range())

    __repr__ = __str__
