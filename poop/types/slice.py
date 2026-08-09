from __future__ import annotations

from typing import TYPE_CHECKING

from poop.types._cloak import cloak
from poop.types.boolean import false, true
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass
    from poop.types.tuple import Tuple

_slice = slice  # alias to avoid shadowing by Slice class name


class Slice(Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(
        self,
        start: Index | NoneClass | None = None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> None:
        self._start: Index | None = _coerce(start)
        self._stop: Index | None = _coerce(stop)
        self._step: Index | None = _coerce(step)

    def start(self) -> Index | NoneClass:
        from poop.types.none import none

        return self._start if self._start is not None else none

    def stop(self) -> Index | NoneClass:
        from poop.types.none import none

        return self._stop if self._stop is not None else none

    def step(self) -> Index | NoneClass:
        from poop.types.none import none

        return self._step if self._step is not None else none

    def _py_slice(self) -> slice:
        # The components go in as they are: `slice` takes any object, and the
        # sequence being sliced resolves each through `__index__`, which Int
        # answers. Reading `._value` here refused a Boolean component and
        # leaked `#_value` for anything else.
        return _slice(self._start, self._stop, self._step)

    def indices(self, length: Index) -> Tuple:
        from poop.types.int import Int
        from poop.types.tuple import Tuple

        start, stop, step = self._py_slice().indices(length)
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
        # Mirror Python's `repr(slice(...))` exactly: lowercase `slice`,
        # always emit all three components (None becomes the literal `None`).
        return (
            f"slice({_field_str(self._start)}, {_field_str(self._stop)}, "
            f"{_field_str(self._step)})"
        )

    __repr__ = __str__


def _resolve_py_slice(
    start_or_slice: Index | Slice | NoneClass | None,
    stop: Index | NoneClass | None,
    step: Index | NoneClass | None,
) -> slice:
    """The native slice a sequence `slice(...)` message resolves to.

    A Slice argument is used directly; the Int form is routed through Slice so
    a POOP `none` stop/step (from a `None` literal) means open-ended, like
    Python's obj[2:]. Shared by List, Tuple, Str, Bytes, ByteArray and Range,
    whose `slice` methods otherwise repeated this branch verbatim.
    """
    if isinstance(start_or_slice, Slice):
        resolved = start_or_slice._py_slice()
    else:
        resolved = Slice(start_or_slice, stop, step)._py_slice()
    # Checked here rather than left to the sequence, which answers `slice
    # indices must be integers or None or have an __index__ method` — naming
    # subscripting and a dunder POOP bans in the same breath, one step after
    # the receiver that would have said which message was sent.
    for bound in (resolved.start, resolved.stop, resolved.step):
        if bound is not None and not hasattr(bound, "__index__"):
            raise MIRRORS["TypeError"](
                f"slice bounds must be int, got a {type(bound).__name__}"
            )
    return resolved


def _coerce(value: Index | NoneClass | None) -> Index | None:
    from poop.types.none import NoneClass

    if value is None or isinstance(value, NoneClass):
        return None
    return value


def _field_eq(a: Index | None, b: Index | None) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return bool(a == b)


def _field_str(value: Index | None) -> str:
    return "None" if value is None else str(value)


cloak(Slice, "slice")
