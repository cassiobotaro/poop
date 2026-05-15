import bisect as _bisect
from collections.abc import Callable
from typing import Any, cast

from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none


def _i(value: Int | None, default: int | None) -> int | None:
    if value is None:
        return default
    return value._value


class Bisect:
    """Namespace mirroring Python's `bisect` module — binary search
    and ordered insertion on sorted POOP `List`s.

    The `bisect` alias maps to `bisect_right` (Python convention).
    Likewise `insort` is `insort_right`. Mutators (`insort_*`) return
    `none` per POOP's mutator convention.

    `key` is a Python callable applied to elements during comparison.
    It receives the underlying POOP element and must return a POOP-
    comparable value.
    """

    @staticmethod
    def bisect_left(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> Int:
        lo_val = _i(lo, 0) or 0
        hi_val = _i(hi, None) or len(a._items)
        items = cast(Any, a._items)
        if key is None:
            return Int(_bisect.bisect_left(items, x, lo_val, hi_val))
        return Int(_bisect.bisect_left(items, x, lo_val, hi_val, key=key))

    @staticmethod
    def bisect_right(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> Int:
        lo_val = _i(lo, 0) or 0
        hi_val = _i(hi, None) or len(a._items)
        items = cast(Any, a._items)
        if key is None:
            return Int(_bisect.bisect_right(items, x, lo_val, hi_val))
        return Int(_bisect.bisect_right(items, x, lo_val, hi_val, key=key))

    @staticmethod
    def bisect(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> Int:
        return Bisect.bisect_right(a, x, lo, hi, key=key)

    @staticmethod
    def insort_left(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> NoneClass:
        lo_val = _i(lo, 0) or 0
        hi_val = _i(hi, None) or len(a._items)
        items = cast(Any, a._items)
        if key is None:
            _bisect.insort_left(items, x, lo_val, hi_val)
        else:
            _bisect.insort_left(items, x, lo_val, hi_val, key=key)
        return none

    @staticmethod
    def insort_right(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> NoneClass:
        lo_val = _i(lo, 0) or 0
        hi_val = _i(hi, None) or len(a._items)
        items = cast(Any, a._items)
        if key is None:
            _bisect.insort_right(items, x, lo_val, hi_val)
        else:
            _bisect.insort_right(items, x, lo_val, hi_val, key=key)
        return none

    @staticmethod
    def insort(
        a: List,
        x: Any,
        lo: Int | None = None,
        hi: Int | None = None,
        *,
        key: Callable[[Any], Any] | None = None,
    ) -> NoneClass:
        return Bisect.insort_right(a, x, lo, hi, key=key)
