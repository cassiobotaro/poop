import builtins
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from reprlib import recursive_repr
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from poop.types._at import at_key, no_key, nothing_to_remove
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._minmax import _MISSING, _minmax
from poop.types._mutated import iterating, reword_if_native
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.dict_items import DictItems
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_keys import DictKeys
from poop.types.dict_values import DictValues
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
    from poop.types.none import NoneClass

_dict = dict  # alias to avoid shadowing by Dict class name in annotations


class Dict(_ValueEqMixin, _IterableMixin, Object):
    """A mapping, and — since proposal 24 — a collection like any other.

    The mixin's messages iterate what CPython iterates, the keys, so
    `d.map(block)` matches `map(f, d)` and `d.items().map(...)` is the
    pair-shaped spelling. `do` stays overridden and yields `Tuple(k, v)`
    pairs, which is how POOP already teaches dict iteration.
    """

    __slots__ = ("_data",)
    _eq_attr: ClassVar[str] = "_data"
    __hash__ = None

    def __init__(self) -> None:
        self._data: _dict[Object, Object] = {}

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

    def at_put(self, key: Object, val: Object) -> Dict:
        self._data[key] = val
        return self

    def includes(self, key: Object) -> Boolean:
        return to_boolean(key in self._data)

    def __eq__(self, other: object) -> Boolean:
        # CPython: ``dict == mappingproxy`` is True by value. A MappingProxy is
        # not a Dict, so _ValueEqMixin would return ``false`` and (being a real
        # value, not NotImplemented) suppress MappingProxy's reflected __eq__.
        # Unwrap the proxy here so the comparison stays symmetric.
        from poop.types.mapping_proxy import MappingProxy

        if isinstance(other, MappingProxy):
            return to_boolean(self._data == other._dict._data)
        # Any Dict (incl. OrderedDict/DefaultDict subclasses) compares by its
        # underlying data. _ValueEqMixin's ``isinstance(other, type(self))`` is
        # asymmetric for subclasses — ``OrderedDict == dict`` would wrongly be
        # ``false`` (and reflected dispatch makes both directions false). The
        # ``_data`` comparison keeps CPython's semantics, including the
        # order-sensitive ``OrderedDict == OrderedDict``.
        if isinstance(other, Dict):
            return to_boolean(self._data == other._data)
        return super().__eq__(other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.mapping_proxy import MappingProxy

        if isinstance(other, MappingProxy):
            return to_boolean(self._data != other._dict._data)
        if isinstance(other, Dict):
            return to_boolean(self._data != other._data)
        return super().__ne__(other)

    @classmethod
    def fromkeys(
        cls, keys: Iterable[Object], value: Object | NoneClass | None = None
    ) -> Dict:
        from poop.types._unwrap import _is_absent

        fill: Object = none if _is_absent(value) else value
        d = cls()
        for k in keys:
            d._data[k] = fill
        return d

    def keys(self) -> DictKeys:
        return DictKeys(self)

    def values(self) -> DictValues:
        return DictValues(self)

    def do(self, block: Callable[[Tuple], Any]) -> NoneClass:
        # Overrides the mixin's to yield pairs, and so needs the same guard:
        # `d.do(lambda p: d.at_put("b", 2))` answered CPython's `dictionary
        # changed size during iteration`.
        try:
            deque((block(Tuple(k, v)) for k, v in self._data.items()), maxlen=0)
        except RuntimeError as exc:
            raise reword_if_native(exc, iterating(self)) from None
        return none

    def min(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(builtins.min, "#min", self._data, key, default)

    def max(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
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

    def clear(self) -> NoneClass:
        self._data.clear()
        return none

    def copy(self) -> Dict:
        new = Dict()
        new._data = self._data.copy()
        return new

    def __or__(self, other: Dict) -> Dict:
        if not isinstance(other, Dict):
            return NotImplemented
        merged = self.copy()
        merged._data.update(other._data)
        return merged

    def __ior__(self, other: object) -> Self:
        # CPython's ``d |= proxy`` updates in place — ``dict.__ior__`` is
        # ``dict.update``, which takes any mapping. A MappingProxy is not a
        # Dict, so returning NotImplemented would hand the operation to
        # MappingProxy's reflected ``__ror__``, rebind the name to a fresh
        # Dict, and silently leave any alias pointing at the unchanged
        # original. Unwrap the proxy here, as ``__eq__`` already does.
        from poop.types.mapping_proxy import MappingProxy

        if isinstance(other, MappingProxy):
            self._data.update(other._dict._data)
            return self
        if not isinstance(other, Dict):
            return NotImplemented
        self._data.update(other._data)
        return self

    def items(self) -> DictItems:
        return DictItems(self)

    def pop(
        self, key: Object, default: Object | NoneClass | Any = _MISSING
    ) -> Object | NoneClass:
        if default is _MISSING:
            # Only the asserting form can fail: `pop(key, default)` answers the
            # default instead, which is why it is left to CPython.
            try:
                return self._data.pop(key)
            except KeyError:
                raise no_key(self, key) from None
        return self._data.pop(key, default)

    def popitem(self) -> Tuple:
        try:
            k, v = self._data.popitem()
        except KeyError:
            raise nothing_to_remove(self) from None
        return Tuple(k, v)

    def setdefault(self, key: Object, default: Object | None = None) -> Object:
        # CPython defaults the fill value to None — `d.setdefault(k)` returns
        # `none` and stores `k: none`, matching `get`/`pop`'s optional default.
        return self._data.setdefault(key, none if default is None else default)

    def update(self, other: Object) -> NoneClass:
        # CPython's dict.update accepts a mapping (Dict / read-only
        # MappingProxy) or an iterable of key/value pairs, e.g.
        # ``d.update([(k1, v1), (k2, v2)])`` — not just another dict.
        from poop.types.mapping_proxy import MappingProxy

        if isinstance(other, Dict):
            self._data.update(other._data)
        elif isinstance(other, MappingProxy):
            self._data.update(other._dict._data)
        else:
            # Each pair is a POOP Tuple — itself a 2-element iterable, so
            # dict.update unpacks it and raises the faithful ValueError on a
            # wrong-length element.
            self._data.update(cast("Iterable[tuple[Object, Object]]", other))
        return none

    # A dict can hold itself as a value — the same cycle `List` guards against,
    # and the same ellipsis CPython prints for it. See the note on `List`.
    @recursive_repr(fillvalue="{...}")
    def __str__(self) -> str:
        pairs = ", ".join(f"{repr(k)}: {repr(v)}" for k, v in self._data.items())
        return "{" + pairs + "}"

    __repr__ = __str__


cloak(Dict, "dict")
