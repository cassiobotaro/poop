from __future__ import annotations

import collections as _collections
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _opt_int
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, to_boolean
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.tuple import Tuple


def _counts_source(arg: Any) -> Any:
    """Coerce a Counter constructor/update argument to stdlib form.

    POOP elements stay as-is inside the impl Counter — they hash and
    compare like the Python values they masquerade as — only a `Dict`
    of counts needs its `Int` values unwrapped to raw ints.
    """
    if arg is None or isinstance(arg, NoneClass):
        return None
    if isinstance(arg, Counter):
        return arg._impl
    if isinstance(arg, Dict):
        return {k: v._value for k, v in arg._data.items()}
    return iter(arg)


class Counter(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Wraps `collections.Counter` — a multiset, Smalltalk's `Bag`.

    Counts hashable elements; missing keys answer `0` instead of
    raising. Elements are stored as POOP objects.
    """

    __slots__ = ("_impl",)

    _eq_attr: ClassVar[str] = "_impl"

    def __init__(self, source: Any = None) -> None:
        src = _counts_source(source)
        if src is None:
            self._impl = _collections.Counter()
        else:
            self._impl = _collections.Counter(src)

    def at(self, key: Object) -> Int:
        return Int(self._impl[key])

    def at_put(self, key: Object, count: Int) -> Counter:
        self._impl[key] = count._value
        return self

    def most_common(self, n: Int | None = None) -> List:
        pairs = self._impl.most_common(_opt_int(n))
        return List(*(Tuple(k, Int(c)) for k, c in pairs))

    def elements(self) -> List:
        return List(*self._impl.elements())

    def total(self) -> Int:
        return Int(self._impl.total())

    def update(self, source: Any) -> NoneClass:
        src = _counts_source(source)
        if src is not None:
            self._impl.update(src)
        return none

    def subtract(self, source: Any) -> NoneClass:
        src = _counts_source(source)
        if src is not None:
            self._impl.subtract(src)
        return none

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def includes(self, key: Object) -> Boolean:
        return to_boolean(key in self._impl)

    def __contains__(self, key: object) -> bool:
        return key in self._impl

    def do(self, block: Any) -> NoneClass:
        # Mirrors Dict.do — the block receives (element, count) pairs.
        _collections.deque(
            (block(Tuple(k, Int(c))) for k, c in self._impl.items()), maxlen=0
        )
        return none

    def __iter__(self) -> Any:
        return iter(self._impl)

    def __add__(self, other: object) -> Counter:
        if not isinstance(other, Counter):
            return NotImplemented
        return Counter._from_impl(self._impl + other._impl)

    def __sub__(self, other: object) -> Counter:
        if not isinstance(other, Counter):
            return NotImplemented
        return Counter._from_impl(self._impl - other._impl)

    def __and__(self, other: object) -> Counter:
        if not isinstance(other, Counter):
            return NotImplemented
        return Counter._from_impl(self._impl & other._impl)

    def __or__(self, other: object) -> Counter:
        if not isinstance(other, Counter):
            return NotImplemented
        return Counter._from_impl(self._impl | other._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__
