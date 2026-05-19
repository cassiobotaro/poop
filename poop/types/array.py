from __future__ import annotations

import array as _array
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.slice import Slice


_INT_TYPECODES = frozenset("bBhHiIlLqQ")
_FLOAT_TYPECODES = frozenset("fd")


def _unwrap_value(typecode: str, value: Object) -> Any:
    if typecode in _INT_TYPECODES:
        if not isinstance(value, Int):
            raise TypeError(
                f"Array typecode {typecode!r} expects Int, got {type(value).__name__}"
            )
        return value._value
    if typecode in _FLOAT_TYPECODES:
        if isinstance(value, Float):
            return value._value
        if isinstance(value, Int):
            return float(value._value)
        raise TypeError(
            f"Array typecode {typecode!r} expects Float, got {type(value).__name__}"
        )
    # Typecode 'u' (Py_UNICODE) was deprecated in 3.12 and is slated
    # for removal — POOP intentionally omits it; use `List[Str]` for
    # character data.
    raise ValueError(f"unsupported typecode {typecode!r}")


def _wrap_value(typecode: str, value: Any) -> Object:
    if typecode in _INT_TYPECODES:
        return Int(value)
    if typecode in _FLOAT_TYPECODES:
        return Float(value)
    raise ValueError(f"unsupported typecode {typecode!r}")


def _initializer_iter(typecode: str, initializer: List | Bytes) -> Any:
    # `array.array` accepts either an iterable of typed values or a
    # bytes-like for binary-loaded typecodes. Mirror that split.
    if isinstance(initializer, Bytes):
        return initializer._value
    if isinstance(initializer, List):
        return [_unwrap_value(typecode, v) for v in initializer]
    raise TypeError(
        f"Array initializer must be List or Bytes, got {type(initializer).__name__}"
    )


class Array(_ValueEqMixin, Object):
    """Wraps Python's `array.array` — a homogeneous, memory-compact
    sequence keyed by a single typecode.

    Integer typecodes (`b`/`B`/`h`/`H`/`i`/`I`/`l`/`L`/`q`/`Q`) take
    `Int`; float typecodes (`f`/`d`) take `Float`. The initializer
    may be a POOP `List` of values or a `Bytes` buffer.

    Typecode `u` (Py_UNICODE) is deprecated upstream and intentionally
    not exposed — use `List[Str]` for character data. `array.fromfile`/
    `tofile` are deferred — POOP has no file-streaming abstraction.
    """

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(self, typecode: Str, initializer: List | Bytes | None = None) -> None:
        code = typecode._value
        if initializer is None:
            self._impl = _array.array(code)
        else:
            self._impl = _array.array(code, _initializer_iter(code, initializer))

    @classmethod
    def _from_impl(cls, impl: _array.array) -> Array:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj

    @property
    def typecode(self) -> Str:
        return Str(self._impl.typecode)

    @property
    def itemsize(self) -> Int:
        return Int(self._impl.itemsize)

    def len(self) -> Int:
        return Int(len(self._impl))

    def __len__(self) -> int:
        return len(self._impl)

    def at(self, index: Int) -> Object:
        return _wrap_value(self._impl.typecode, self._impl[index._value])

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> Array:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            return Array._from_impl(self._impl[start_or_slice._py_slice()])
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return Array._from_impl(self._impl[start_or_slice._value : stop._value : s])

    def append(self, value: Object) -> NoneClass:
        self._impl.append(_unwrap_value(self._impl.typecode, value))
        return none

    def extend(self, other: List | Array) -> NoneClass:
        if isinstance(other, Array):
            self._impl.extend(other._impl)
        else:
            for v in other:
                self._impl.append(_unwrap_value(self._impl.typecode, v))
        return none

    def insert(self, i: Int, value: Object) -> NoneClass:
        self._impl.insert(i._value, _unwrap_value(self._impl.typecode, value))
        return none

    def pop(self, i: Int | NoneClass | None = None) -> Object:
        from poop.types._unwrap import _is_absent

        if _is_absent(i):
            value = self._impl.pop()
        else:
            value = self._impl.pop(i._value)  # ty: ignore[unresolved-attribute]
        return _wrap_value(self._impl.typecode, value)

    def remove(self, value: Object) -> NoneClass:
        self._impl.remove(_unwrap_value(self._impl.typecode, value))
        return none

    def count(self, value: Object) -> Int:
        return Int(self._impl.count(_unwrap_value(self._impl.typecode, value)))

    def index(self, value: Object) -> Int:
        return Int(self._impl.index(_unwrap_value(self._impl.typecode, value)))

    def reverse(self) -> NoneClass:
        self._impl.reverse()
        return none

    def tobytes(self) -> Bytes:
        return Bytes(self._impl.tobytes())

    def tolist(self) -> List:
        code = self._impl.typecode
        return List(*(_wrap_value(code, v) for v in self._impl))

    def frombytes(self, buf: Bytes) -> NoneClass:
        self._impl.frombytes(buf._value)
        return none

    def fromlist(self, items: List) -> NoneClass:
        code = self._impl.typecode
        for v in items:
            self._impl.append(_unwrap_value(code, v))
        return none

    def do(self, block: Callable[[Object], Any]) -> NoneClass:
        code = self._impl.typecode
        for v in self._impl:
            block(_wrap_value(code, v))
        return none

    def __iter__(self) -> Any:
        code = self._impl.typecode
        for v in self._impl:
            yield _wrap_value(code, v)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Object):
            return False
        try:
            unwrapped = _unwrap_value(self._impl.typecode, item)
        except TypeError:
            return False
        return unwrapped in self._impl

    def includes(self, value: Object) -> Boolean:
        try:
            unwrapped = _unwrap_value(self._impl.typecode, value)
        except TypeError:
            return false
        return true if unwrapped in self._impl else false

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class ArrayNamespace:
    """Namespace mirroring Python's `array` module.

    `array.typecodes` is the string of valid typecodes; the `Array`
    class is exposed alongside this namespace for construction.
    """

    typecodes: ClassVar[Str] = Str(_array.typecodes)
    ArrayType: ClassVar[type[Array]] = Array
