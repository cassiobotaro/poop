import builtins
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar, Self

from poop.types._iterable_mixin import _MISSING
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
    from poop.types.enumerate import Enumerate
    from poop.types.none import NoneClass
    from poop.types.zip import Zip

_dict = dict  # alias to avoid shadowing by Dict class name in annotations


class Dict(_ValueEqMixin, Object):
    __slots__ = ("_data",)
    _eq_attr: ClassVar[str] = "_data"
    __hash__ = None

    def __init__(self) -> None:
        self._data: _dict[Object, Object] = {}

    def at(self, key: Object) -> Object:
        return self._data[key]

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
        deque((block(Tuple(k, v)) for k, v in self._data.items()), maxlen=0)
        return none

    def min(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return builtins.min(self._data, **kwargs)

    def max(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return builtins.max(self._data, **kwargs)

    def len(self) -> Int:
        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def iter(self) -> DictKeyIterator:
        return DictKeyIterator(self._data)

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

    def __ior__(self, other: Dict) -> Self:
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
            return self._data.pop(key)
        return self._data.pop(key, default)

    def popitem(self) -> Tuple:
        k, v = self._data.popitem()
        return Tuple(k, v)

    def setdefault(self, key: Object, default: Object | None = None) -> Object:
        # CPython defaults the fill value to None — `d.setdefault(k)` returns
        # `none` and stores `k: none`, matching `get`/`pop`'s optional default.
        return self._data.setdefault(key, none if default is None else default)

    def update(self, other: Dict) -> NoneClass:
        self._data.update(other._data)
        return none

    def enumerate(self, start: Int | NoneClass | None = None) -> Enumerate:
        from poop.types.enumerate import Enumerate

        return Enumerate(self, start)

    def zip(self, *others: Object, strict: Boolean | NoneClass | None = None) -> Zip:
        from poop.types.zip import Zip

        return Zip(self, *others, strict=strict)

    def __str__(self) -> str:
        pairs = ", ".join(f"{repr(k)}: {repr(v)}" for k, v in self._data.items())
        return "{" + pairs + "}"

    __repr__ = __str__


Dict.__module__ = "builtins"
Dict.__name__ = "dict"
