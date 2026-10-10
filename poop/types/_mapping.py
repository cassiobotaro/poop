"""The read side of a mapping, shared by `Dict` and `FrozenDict`.

The same move `_BytesLikeMixin` makes for `bytes` and `bytearray`: Python 3.15's
`frozendict` answers exactly `dict`'s read messages (`get`, `keys`, `values`,
`items`, `copy`, `fromkeys`, and the protocol behind `at`, `includes`, `len`
and iteration) and none of its writes, so the read side is written once here
and each class keeps what really differs — `Dict` its mutators and `|=`,
`FrozenDict` its hash, and each its own `|` and repr.

Every message reads `_data`, the raw `dict` the concrete class declares as its
slot; `_wrapping` builds a class over one that call hands over.
"""

import builtins
from typing import TYPE_CHECKING, ClassVar, Self, overload

from poop.types._argument import Key, a_collection
from poop.types._at import at_key
from poop.types._iterable_mixin import _IterableMixin
from poop.types._minmax import _minmax
from poop.types._sentinel import MISSING, Missing
from poop.types._unwrap import _is_absent
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.dict_items import DictItems
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_keys import DictKeys
from poop.types.dict_values import DictValues
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from poop.types.boolean import Boolean
    from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
    from poop.types.none import NoneClass


class _MappingMixin(_ValueEqMixin, _IterableMixin[Object], Object, name="dict"):  # noqa: PLW1641 — each class hashes by value or not at all
    """A mapping, and a collection like any other.

    The iterable mixin's messages iterate what CPython iterates, the keys, so
    `d.map(block)` matches `map(f, d)` and `d.items().map(...)` is the
    pair-shaped spelling.
    """

    __slots__ = ()
    _data: dict[Object, Object]
    _eq_attr: ClassVar[str] = "_data"
    # `dict == frozendict` is True by value in CPython, both ways, as `set ==
    # frozenset` is; the group is what lets `_ValueEqMixin` say so.
    _eq_group: ClassVar[str] = "mapping"

    @classmethod
    def _wrapping(cls, data: dict[Object, Object]) -> Self:
        """A `cls` over `data`, a raw dict this call hands over."""
        wrapped = cls()
        wrapped._data = data
        return wrapped

    def at(self, key: Object) -> Object:
        return at_key(self._data, key, self)

    def __getitem__(self, key: Object) -> Object:
        # Satisfies the mapping protocol (`{**d}` merge / `**d` unpacking
        # read `d[k]`). User subscript syntax stays forbidden by no_subscript.
        return self._data[key]

    def get(
        self, key: Object, default: Object | NoneClass = none
    ) -> Object | NoneClass:
        return self._data.get(key, default)

    def includes(self, key: Object) -> Boolean:
        return to_boolean(key in self)

    def __eq__(self, other: object) -> Boolean:
        # CPython: ``dict == mappingproxy`` is True by value. A MappingProxy is
        # not a mapping here, so _ValueEqMixin would return ``false`` and
        # (being a real value, not NotImplemented) suppress MappingProxy's
        # reflected __eq__. Unwrap the proxy here so the comparison stays
        # symmetric.
        if isinstance(other, MappingProxy):
            return to_boolean(self._data == other._dict._data)
        # Any mapping (incl. OrderedDict/DefaultDict subclasses, and the
        # frozen kind) compares by its underlying data. _ValueEqMixin's
        # ``isinstance(other, type(self))`` is asymmetric for subclasses —
        # ``OrderedDict == dict`` would wrongly be ``false`` (and reflected
        # dispatch makes both directions false). The ``_data`` comparison
        # keeps CPython's semantics, including the order-sensitive
        # ``OrderedDict == OrderedDict``.
        if isinstance(other, _MappingMixin):
            return to_boolean(self._data == other._data)
        return super().__eq__(other)

    @classmethod
    def fromkeys(
        cls, keys: Iterable[Object], value: Object | NoneClass | None = None
    ) -> Self:
        fill: Object = none if _is_absent(value) else value
        return cls._wrapping(dict.fromkeys(a_collection(keys, "fromkeys"), fill))

    def copy(self) -> Self:
        # Left to each class: a `Dict` copies, a `FrozenDict` answers itself.
        raise NotImplementedError

    def keys(self) -> DictKeys:
        return DictKeys(self)

    def values(self) -> DictValues:
        return DictValues(self)

    def items(self) -> DictItems:
        return DictItems(self)

    # `do` is deliberately *not* overridden here. It used to yield `(key,
    # value)` pairs while `map`, `filter`, `sorted`, `min`, `max` and `iter`
    # on the same receiver all yielded keys — one receiver with two answers to
    # "what is an element of a dict", and the odd one out was the message
    # `no_loops` names as the substitute for `for k in d`, which walks the
    # keys in Python. The mixin's `do` walks `__iter__` like its five
    # siblings, and carries the same mutation guard, worded from the receiver.
    # `d.items().do(...)` is the pair spelling, and answers `Tuple`s already.

    @overload
    def min(self, *, key: Key[Object] = None) -> Object: ...
    @overload
    def min[D](self, *, key: Key[Object] = None, default: D) -> Object | D: ...
    def min[D](
        self, *, key: Key[Object] = None, default: D | Missing = MISSING
    ) -> Object | D:
        return _minmax(builtins.min, "#min", self._data, key, default)

    @overload
    def max(self, *, key: Key[Object] = None) -> Object: ...
    @overload
    def max[D](self, *, key: Key[Object] = None, default: D) -> Object | D: ...
    def max[D](
        self, *, key: Key[Object] = None, default: D | Missing = MISSING
    ) -> Object | D:
        return _minmax(builtins.max, "#max", self._data, key, default)

    def len(self) -> Int:
        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def iter(self) -> DictKeyIterator:
        return DictKeyIterator(self._data)

    def reversed(self) -> DictReverseKeyIterator:
        # `reversed(d)` yields the keys in reverse in CPython, which is what
        # `d.keys().reversed()` already answered — the receiver `no_reversed`
        # names had no substitute of its own.
        return self.keys().reversed()

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def _pairs(self) -> str:
        """`k: v, …` — the body of both reprs."""
        return ", ".join(f"{k!r}: {v!r}" for k, v in self._data.items())
