from __future__ import annotations

import struct as _struct
from typing import Any, ClassVar

from poop.types._unwrap import _kwargs_from
from poop.types.boolean import Boolean, to_boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.memory_view import MemoryView
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_value(value: Any) -> Any:
    if isinstance(value, Int | Float | Str | Bytes):
        return value._value
    if isinstance(value, Boolean):
        return bool(value)
    if isinstance(value, ByteArray):
        return bytes(value._value)
    return value


def _wrap_value(value: Any) -> Object:
    if isinstance(value, bool):
        return to_boolean(value)
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, bytes):
        return Bytes(value)
    if isinstance(value, str):
        return Str(value)
    return value


def _read_buffer(buffer: Bytes | ByteArray | MemoryView) -> Any:
    if isinstance(buffer, Bytes):
        return buffer._value
    if isinstance(buffer, ByteArray):
        return buffer._value
    if isinstance(buffer, MemoryView):
        return buffer._value
    raise TypeError(
        f"struct buffer must be Bytes / ByteArray / MemoryView, got {type(buffer).__name__}"
    )


def _writable_buffer(buffer: ByteArray | MemoryView) -> Any:
    # pack_into needs a writable buffer; Bytes is immutable upstream.
    if isinstance(buffer, ByteArray):
        return buffer._value
    if isinstance(buffer, MemoryView):
        return buffer._value
    raise TypeError(
        f"struct.pack_into requires a writable buffer (ByteArray or MemoryView), got {type(buffer).__name__}"
    )


def _wrap_tuple(raw: tuple[Any, ...]) -> Tuple:
    return Tuple(*(_wrap_value(v) for v in raw))


class Struct:
    """Wraps Python's `struct.Struct` — a pre-compiled format object.

    Same surface as the module-level shortcuts (`pack` / `unpack` /
    `pack_into` / `unpack_from` / `iter_unpack`) plus `.format` and
    `.size`. Reusing a `Struct` instance avoids recompiling the format
    string on each call.
    """

    __slots__ = ("_impl",)

    def __init__(self, format: Str) -> None:
        self._impl = _struct.Struct(format._value)

    @property
    def format(self) -> Str:
        return Str(self._impl.format)

    @property
    def size(self) -> Int:
        return Int(self._impl.size)

    def pack(self, *values: Object) -> Bytes:
        return Bytes(self._impl.pack(*(_unwrap_value(v) for v in values)))

    def unpack(self, buffer: Bytes | ByteArray | MemoryView) -> Tuple:
        return _wrap_tuple(self._impl.unpack(_read_buffer(buffer)))

    def pack_into(
        self,
        buffer: ByteArray | MemoryView,
        offset: Int,
        *values: Object,
    ) -> NoneClass:
        self._impl.pack_into(
            _writable_buffer(buffer),
            offset._value,
            *(_unwrap_value(v) for v in values),
        )
        return none

    def unpack_from(
        self,
        buffer: Bytes | ByteArray | MemoryView,
        offset: Int | None = None,
    ) -> Tuple:
        kwargs = _kwargs_from(offset=offset)
        return _wrap_tuple(self._impl.unpack_from(_read_buffer(buffer), **kwargs))

    def iter_unpack(self, buffer: Bytes | ByteArray | MemoryView) -> List:
        # POOP collections aren't lazy — materialize.
        return List(
            *(_wrap_tuple(t) for t in self._impl.iter_unpack(_read_buffer(buffer)))
        )


class StructNamespace:
    """Namespace mirroring Python's `struct` module.

    Module-level shortcuts (`pack` / `unpack` / `pack_into` /
    `unpack_from` / `iter_unpack` / `calcsize`) plus the `Struct`
    class for reusable formats. `struct.error` is exposed as a class
    attribute for use with `Try.except_`.
    """

    Struct: ClassVar[type[Struct]] = Struct
    error: ClassVar[type[Exception]] = _struct.error

    @staticmethod
    def pack(format: Str, *values: Object) -> Bytes:
        return Bytes(_struct.pack(format._value, *(_unwrap_value(v) for v in values)))

    @staticmethod
    def unpack(format: Str, buffer: Bytes | ByteArray | MemoryView) -> Tuple:
        return _wrap_tuple(_struct.unpack(format._value, _read_buffer(buffer)))

    @staticmethod
    def pack_into(
        format: Str,
        buffer: ByteArray | MemoryView,
        offset: Int,
        *values: Object,
    ) -> NoneClass:
        _struct.pack_into(
            format._value,
            _writable_buffer(buffer),
            offset._value,
            *(_unwrap_value(v) for v in values),
        )
        return none

    @staticmethod
    def unpack_from(
        format: Str,
        buffer: Bytes | ByteArray | MemoryView,
        offset: Int | None = None,
    ) -> Tuple:
        kwargs = _kwargs_from(offset=offset)
        return _wrap_tuple(
            _struct.unpack_from(format._value, _read_buffer(buffer), **kwargs)
        )

    @staticmethod
    def iter_unpack(format: Str, buffer: Bytes | ByteArray | MemoryView) -> List:
        return List(
            *(
                _wrap_tuple(t)
                for t in _struct.iter_unpack(format._value, _read_buffer(buffer))
            )
        )

    @staticmethod
    def calcsize(format: Str) -> Int:
        return Int(_struct.calcsize(format._value))
