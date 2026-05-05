from __future__ import annotations

from typing import TYPE_CHECKING

from poop.types.boolean import false, true
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.tuple import Tuple

_slice = slice  # alias to avoid shadowing by Slice class name


class Slice(Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(self, start: Int, stop: Int, step: Int | None = None) -> None:
        self._start = start
        self._stop = stop
        self._step = step

    def start(self) -> Int:
        return self._start

    def stop(self) -> Int:
        return self._stop

    def step(self) -> Int | NoneClass:
        from poop.types.none import none

        return self._step if self._step is not None else none

    def indices(self, length: Int) -> Tuple:
        from poop.types.int import Int
        from poop.types.tuple import Tuple

        step = self._step._value if self._step is not None else None
        start, stop, step = _slice(self._start._value, self._stop._value, step).indices(
            length._value
        )
        return Tuple(Int(start), Int(stop), Int(step))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, Slice):
            if self._step is None and other._step is None:
                step_eq = True
            elif self._step is not None and other._step is not None:
                step_eq = bool(self._step == other._step)
            else:
                step_eq = False
            return (
                true
                if bool(self._start == other._start)
                and bool(self._stop == other._stop)
                and step_eq
                else false
            )
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, Slice):
            return false if bool(self == other) else true
        return true

    def __hash__(self) -> int:
        return hash((self._start, self._stop, self._step))

    def __str__(self) -> str:
        if self._step is None:
            return f"Slice({self._start}, {self._stop})"
        return f"Slice({self._start}, {self._stop}, {self._step})"

    __repr__ = __str__
