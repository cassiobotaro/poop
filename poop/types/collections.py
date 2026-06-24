from __future__ import annotations

import collections as _collections
from typing import Any, ClassVar, cast

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _b, _opt_int
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, to_boolean
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
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


class Deque(_ImplWrapperMixin, _ValueEqMixin, _IterableMixin, Object):
    """Wraps `collections.deque` — Smalltalk's `OrderedCollection`.

    A double-ended queue with O(1) appends and pops on both sides.
    Items are stored as POOP objects.
    """

    __slots__ = ("_impl",)

    _eq_attr: ClassVar[str] = "_impl"

    def __init__(self, source: Any = None, maxlen: Int | None = None) -> None:
        items = () if source is None or isinstance(source, NoneClass) else iter(source)
        self._impl: _collections.deque[Object] = _collections.deque(
            items, _opt_int(maxlen)
        )

    def append(self, item: Object) -> NoneClass:
        self._impl.append(item)
        return none

    def appendleft(self, item: Object) -> NoneClass:
        self._impl.appendleft(item)
        return none

    def pop(self) -> Any:
        return self._impl.pop()

    def popleft(self) -> Any:
        return self._impl.popleft()

    def extend(self, source: Any) -> NoneClass:
        self._impl.extend(iter(source))
        return none

    def extendleft(self, source: Any) -> NoneClass:
        self._impl.extendleft(iter(source))
        return none

    def insert(self, index: Int, item: Object) -> NoneClass:
        self._impl.insert(index._value, item)
        return none

    def index(
        self,
        item: Object,
        start: Int | NoneClass | None = None,
        stop: Int | NoneClass | None = None,
    ) -> Int:
        s = _opt_int(start, 0)
        if stop is None or isinstance(stop, NoneClass):
            return Int(self._impl.index(item, s))
        return Int(self._impl.index(item, s, stop._value))

    def copy(self) -> Deque:
        return Deque._from_impl(self._impl.copy())

    def __add__(self, other: object) -> Deque:
        if not isinstance(other, Deque):
            return NotImplemented
        return Deque._from_impl(self._impl + other._impl)

    def __mul__(self, n: object) -> Deque:
        if not isinstance(n, Int):
            return NotImplemented
        return Deque._from_impl(self._impl * n._value)

    def rotate(self, n: Int | NoneClass | None = None) -> NoneClass:
        self._impl.rotate(_opt_int(n, 1))
        return none

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none

    def count(self, item: Object) -> Int:
        return Int(self._impl.count(item))

    def remove(self, item: Object) -> NoneClass:
        self._impl.remove(item)
        return none

    def reverse(self) -> NoneClass:
        self._impl.reverse()
        return none

    def at(self, index: Int) -> Any:
        return self._impl[index._value]

    @property
    def maxlen(self) -> Int | NoneClass:
        m = self._impl.maxlen
        return none if m is None else Int(m)

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def includes(self, item: Object) -> Boolean:
        return to_boolean(item in self._impl)

    def __contains__(self, item: object) -> bool:
        return item in self._impl

    def __iter__(self) -> Any:
        return iter(self._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class DefaultDict(Dict):
    """Wraps `collections.defaultdict` behind the full `Dict` surface.

    The default factory is a block (`lambda: List()`); `at` on a
    missing key calls it, stores the result, and answers it — no
    `KeyError`, no bridging, since blocks already return POOP values.
    """

    __slots__ = ()

    def __init__(self, default_factory: Any = None, source: Dict | None = None) -> None:
        factory = (
            None
            if default_factory is None or isinstance(default_factory, NoneClass)
            else default_factory
        )
        self._data = _collections.defaultdict(factory)
        if source is not None and not isinstance(source, NoneClass):
            self._data.update(source._data)

    @property
    def default_factory(self) -> Any:
        impl = cast("_collections.defaultdict[Object, Object]", self._data)
        return none if impl.default_factory is None else impl.default_factory

    def copy(self) -> DefaultDict:
        new = DefaultDict.__new__(DefaultDict)
        new._data = self._data.copy()
        return new


class OrderedDict(Dict):
    """Wraps `collections.OrderedDict` — a `Dict` that can reorder:
    `move_to_end` and a directional `popitem`."""

    __slots__ = ()

    def __init__(self, source: Dict | None = None) -> None:
        self._data = _collections.OrderedDict()
        if source is not None and not isinstance(source, NoneClass):
            self._data.update(source._data)

    def _ordered(self) -> _collections.OrderedDict[Object, Object]:
        return cast("_collections.OrderedDict[Object, Object]", self._data)

    def move_to_end(
        self, key: Object, last: Boolean | NoneClass | None = None
    ) -> NoneClass:
        self._ordered().move_to_end(key, _b(last, True))
        return none

    def popitem(self, last: Boolean | NoneClass | None = None) -> Tuple:
        k, v = self._ordered().popitem(_b(last, True))
        return Tuple(k, v)

    def copy(self) -> OrderedDict:
        new = OrderedDict()
        new._data.update(self._data)
        return new


class ChainMap(_ValueEqMixin, Object):
    """Wraps `collections.ChainMap` — a lookup chain over POOP `Dict`s.

    Reads search each map in order; writes land on the first map. The
    chain is live: mutating an underlying `Dict` is visible through
    the chain immediately.
    """

    __slots__ = ("_impl", "_maps")

    _eq_attr: ClassVar[str] = "_impl"

    def __init__(self, *maps: Dict) -> None:
        bad = next((m for m in maps if not isinstance(m, Dict)), None)
        if bad is not None:
            raise TypeError(
                f"ChainMap maps must be dicts, got {type(bad).__qualname__}"
            )
        self._maps: list[Dict] = list(maps) if maps else [Dict()]
        self._impl = _collections.ChainMap(*(m._data for m in self._maps))

    def at(self, key: Object) -> Object:
        return self._impl[key]

    def get(self, key: Object, default: Object | NoneClass = none) -> Any:
        return self._impl.get(key, default)

    def at_put(self, key: Object, val: Object) -> ChainMap:
        self._impl[key] = val
        return self

    def includes(self, key: Object) -> Boolean:
        return to_boolean(key in self._impl)

    def __contains__(self, key: object) -> bool:
        return key in self._impl

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def __iter__(self) -> Any:
        return iter(self._impl)

    def do(self, block: Any) -> NoneClass:
        # Mirrors Dict.do — the block receives (key, value) pairs.
        _collections.deque(
            (block(Tuple(k, v)) for k, v in self._impl.items()), maxlen=0
        )
        return none

    @property
    def maps(self) -> List:
        return List(*self._maps)

    def new_child(self, m: Dict | NoneClass | None = None) -> ChainMap:
        front = Dict() if m is None or isinstance(m, NoneClass) else m
        return ChainMap(front, *self._maps)

    @property
    def parents(self) -> ChainMap:
        return ChainMap(*self._maps[1:])

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


def _namedtuple_namespace(name: str, fields: list[str]) -> dict[str, Any]:
    def _make_property(index: int) -> property:
        return property(lambda self: self._items[index])

    def _nt_init(self: Tuple, *elements: Object) -> None:
        if len(elements) != len(fields):
            raise TypeError(
                f"{name} expects {len(fields)} arguments, got {len(elements)}"
            )
        Tuple.__init__(self, *elements)

    def _nt_str(self: Tuple) -> str:
        pairs = ", ".join(f"{f}={self._items[i]!r}" for i, f in enumerate(fields))
        return f"{name}({pairs})"

    def _nt_make(cls: type, iterable: Any) -> Any:
        return cls(*iterable)

    def _nt_asdict(self: Tuple) -> Dict:
        d = Dict()
        for i, f in enumerate(fields):
            d.at_put(Str(f), self._items[i])
        return d

    def _nt_replace(self: Tuple, **changes: Any) -> Any:
        unexpected = set(changes) - set(fields)
        if unexpected:
            raise ValueError(f"got unexpected field names: {sorted(unexpected)!r}")
        values = (changes.get(f, self._items[i]) for i, f in enumerate(fields))
        return type(self)(*values)

    namespace: dict[str, Any] = {f: _make_property(i) for i, f in enumerate(fields)}
    namespace["__slots__"] = ()
    namespace["__init__"] = _nt_init
    namespace["__str__"] = _nt_str
    namespace["__repr__"] = _nt_str
    namespace["_fields"] = Tuple(*(Str(f) for f in fields))
    namespace["_make"] = classmethod(_nt_make)
    namespace["_asdict"] = _nt_asdict
    namespace["_replace"] = _nt_replace
    return namespace


def namedtuple(typename: Str, field_names: Any) -> type:
    """Build a lightweight value class — a `Tuple` subclass whose
    fields read as properties (`p.x`), mirroring `collections.namedtuple`
    without decorator or metaclass syntax.

    `field_names` is a `Str` (`"x y"` or `"x, y"`) or an iterable of
    `Str`.
    """
    name = typename._value
    if isinstance(field_names, Str):
        fields = field_names._value.replace(",", " ").split()
    else:
        fields = [f._value for f in field_names]
    bad = [f for f in fields if not f.isidentifier()]
    if bad:
        raise ValueError(f"field names must be valid identifiers: {bad[0]!r}")
    if len(set(fields)) != len(fields):
        raise ValueError("field names must be unique")
    return type(name, (Tuple,), _namedtuple_namespace(name, fields))


class CollectionsNamespace:
    """Namespace mirroring Python's `collections` module."""

    Counter: ClassVar[type[Counter]] = Counter
    deque: ClassVar[type[Deque]] = Deque
    defaultdict: ClassVar[type[DefaultDict]] = DefaultDict
    OrderedDict: ClassVar[type[OrderedDict]] = OrderedDict
    ChainMap: ClassVar[type[ChainMap]] = ChainMap
    namedtuple = staticmethod(namedtuple)
