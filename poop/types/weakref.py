from __future__ import annotations

import weakref as _weakref
from collections.abc import Callable, Iterable, Iterator
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object


def _wrap_callback(
    callback: Callable[..., Any] | None,
) -> Callable[[Any], None] | None:
    if callback is None:
        return None

    def adapter(_dead_ref: Any) -> None:
        callback(none)

    return adapter


class WeakRef(Object):
    """Wraps Python's `weakref.ref`.

    `WeakRef(obj, callback=none)` keeps a weak reference; calling the
    instance (or `.get()`) returns the live object or `none` once the
    referent has been garbage-collected. `callback` is fired with
    `none` when the referent dies.
    """

    __slots__ = ("_impl",)

    def __init__(self, obj: Object, callback: Callable[..., Any] | None = None) -> None:
        self._impl = _weakref.ref(obj, _wrap_callback(callback))

    def get(self) -> Object | NoneClass:
        live = self._impl()
        if live is None:
            return none
        return live

    def __call__(self) -> Object | NoneClass:
        return self.get()

    def is_alive(self) -> Boolean:
        return true if self._impl() is not None else false


class WeakSet(Object):
    """Wraps Python's `weakref.WeakSet`.

    A set whose entries are weakly referenced — items disappear once
    the only strong reference to them goes away.
    """

    __slots__ = ("_impl",)

    def __init__(self, items: Iterable[Object] | None = None) -> None:
        if items is None:
            self._impl = _weakref.WeakSet()
        else:
            self._impl = _weakref.WeakSet(items)

    def add(self, obj: Object) -> NoneClass:
        self._impl.add(obj)
        return none

    def discard(self, obj: Object) -> NoneClass:
        self._impl.discard(obj)
        return none

    def remove(self, obj: Object) -> NoneClass:
        self._impl.remove(obj)
        return none

    def includes(self, obj: Object) -> Boolean:
        return true if obj in self._impl else false

    def __contains__(self, obj: object) -> bool:
        return obj in self._impl

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._impl)

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none

    def copy(self) -> WeakSet:
        new = WeakSet()
        new._impl = self._impl.copy()
        return new


class WeakKeyDictionary(Object):
    """Wraps Python's `weakref.WeakKeyDictionary`.

    A dict whose keys are weakly referenced — entries vanish once the
    key has no other strong references.
    """

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _weakref.WeakKeyDictionary()

    def at(self, key: Object) -> Object:
        return self._impl[key]

    def at_put(self, key: Object, value: Object) -> WeakKeyDictionary:
        self._impl[key] = value
        return self

    def get(
        self, key: Object, default: Object | NoneClass = none
    ) -> Object | NoneClass:
        return self._impl.get(key, default)

    def includes(self, key: Object) -> Boolean:
        return true if key in self._impl else false

    def __contains__(self, key: object) -> bool:
        return key in self._impl

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._impl)

    def keys(self) -> List:
        return List(*self._impl.keys())

    def values(self) -> List:
        return List(*self._impl.values())

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none


class WeakValueDictionary(Object):
    """Wraps Python's `weakref.WeakValueDictionary`.

    A dict whose values are weakly referenced — entries vanish once
    the value has no other strong references.
    """

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _weakref.WeakValueDictionary()

    def at(self, key: Object) -> Object:
        return self._impl[key]

    def at_put(self, key: Object, value: Object) -> WeakValueDictionary:
        self._impl[key] = value
        return self

    def get(
        self, key: Object, default: Object | NoneClass = none
    ) -> Object | NoneClass:
        return self._impl.get(key, default)

    def includes(self, key: Object) -> Boolean:
        return true if key in self._impl else false

    def __contains__(self, key: object) -> bool:
        return key in self._impl

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._impl)

    def keys(self) -> List:
        return List(*self._impl.keys())

    def values(self) -> List:
        return List(*self._impl.values())

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none


class Weakref:
    """Namespace mirroring Python's `weakref` module.

    Weak references let an object be garbage-collected even while a
    reference to it is kept — useful for caches and breaking cycles.
    `WeakRef` is exposed bare alongside the namespace (matching the
    `UUID` / `HMAC` convention); `WeakSet` / `WeakKeyDictionary` /
    `WeakValueDictionary` are the collection variants.

    `finalize` and `WeakMethod` are out of scope for v1.

    Note: only POOP user-class instances (and `List` / `Set` /
    `Dict` / `Tuple` whose classes carry `__weakref__`) can be
    referenced. Built-in primitives like `Int` / `Str` define
    `__slots__` without `__weakref__`, matching Python's restriction
    on weakref'ing `int` / `str`.
    """

    WeakRef: ClassVar[type[WeakRef]] = WeakRef
    WeakSet: ClassVar[type[WeakSet]] = WeakSet
    WeakKeyDictionary: ClassVar[type[WeakKeyDictionary]] = WeakKeyDictionary
    WeakValueDictionary: ClassVar[type[WeakValueDictionary]] = WeakValueDictionary

    ReferenceType: ClassVar[type[WeakRef]] = WeakRef

    @staticmethod
    def ref(obj: Object, callback: Callable[..., Any] | None = None) -> WeakRef:
        return WeakRef(obj, callback)

    @staticmethod
    def proxy(obj: Object, callback: Callable[..., Any] | None = None) -> Any:
        # CPython's proxy is a transparent forwarder, not a POOP wrapper.
        # Returning it raw means messages forward to the underlying
        # object as long as the proxy is alive.
        return _weakref.proxy(obj, _wrap_callback(callback))

    @staticmethod
    def getweakrefcount(obj: Object) -> Int:
        return Int(_weakref.getweakrefcount(obj))

    @staticmethod
    def getweakrefs(obj: Object) -> List:
        refs = _weakref.getweakrefs(obj)
        wrapped: list[Object] = []
        for r in refs:
            w = WeakRef.__new__(WeakRef)
            w._impl = r
            wrapped.append(w)
        return List(*wrapped)
