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

    def __init__(
        self,
        start: Int | NoneClass | None = None,
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> None:
        self._start: Int | None = _coerce(start)
        self._stop: Int | None = _coerce(stop)
        self._step: Int | None = _coerce(step)

    def start(self) -> Int | NoneClass:
        from poop.types.none import none

        return self._start if self._start is not None else none

    def stop(self) -> Int | NoneClass:
        from poop.types.none import none

        return self._stop if self._stop is not None else none

    def step(self) -> Int | NoneClass:
        from poop.types.none import none

        return self._step if self._step is not None else none

    def _py_slice(self) -> slice:
        return _slice(
            self._start._value if self._start is not None else None,
            self._stop._value if self._stop is not None else None,
            self._step._value if self._step is not None else None,
        )

    def indices(self, length: Int) -> Tuple:
        from poop.types.int import Int
        from poop.types.tuple import Tuple

        start, stop, step = self._py_slice().indices(length._value)
        return Tuple(Int(start), Int(stop), Int(step))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, Slice):
            if (
                _field_eq(self._start, other._start)
                and _field_eq(self._stop, other._stop)
                and _field_eq(self._step, other._step)
            ):
                return true
            return false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, Slice):
            return false if bool(self == other) else true
        return true

    def __hash__(self) -> int:
        return hash((self._start, self._stop, self._step))

    def __str__(self) -> str:
        if self._step is None:
            return f"Slice({_field_str(self._start)}, {_field_str(self._stop)})"
        return (
            f"Slice({_field_str(self._start)}, {_field_str(self._stop)}, "
            f"{_field_str(self._step)})"
        )

    __repr__ = __str__


def _coerce(value: Int | NoneClass | None) -> Int | None:
    from poop.types.none import NoneClass

    if value is None or isinstance(value, NoneClass):
        return None
    return value


def _field_eq(a: Int | None, b: Int | None) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return bool(a == b)


def _field_str(value: Int | None) -> str:
    return "None" if value is None else str(value)


Slice.__module__ = "builtins"
Slice.__name__ = "slice"
