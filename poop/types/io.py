from __future__ import annotations

import io as _io
from typing import ClassVar, Self

from poop.types._unwrap import _kwargs_from
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


class StringIO(Object):
    """Wraps Python's `io.StringIO` — in-memory text buffer."""

    __slots__ = ("_impl",)

    def __init__(
        self, initial_value: Str | None = None, newline: Str | None = None
    ) -> None:
        kwargs = _kwargs_from(initial_value=initial_value, newline=newline)
        self._impl = _io.StringIO(**kwargs)

    def read(self, size: Int | None = None) -> Str:
        if size is None:
            return Str(self._impl.read())
        return Str(self._impl.read(size._value))

    def readline(self, size: Int | None = None) -> Str:
        if size is None:
            return Str(self._impl.readline())
        return Str(self._impl.readline(size._value))

    def write(self, s: Str) -> Int:
        return Int(self._impl.write(s._value))

    def getvalue(self) -> Str:
        return Str(self._impl.getvalue())

    def seek(self, pos: Int, whence: Int | None = None) -> Int:
        w = 0 if whence is None else whence._value
        return Int(self._impl.seek(pos._value, w))

    def tell(self) -> Int:
        return Int(self._impl.tell())

    def truncate(self, size: Int | None = None) -> Int:
        s = None if size is None else size._value
        return Int(self._impl.truncate(s))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.close()


class BytesIO(Object):
    """Wraps Python's `io.BytesIO` — in-memory binary buffer."""

    __slots__ = ("_impl",)

    def __init__(self, initial_bytes: Bytes | None = None) -> None:
        b = b"" if initial_bytes is None else initial_bytes._value
        self._impl = _io.BytesIO(b)

    def read(self, size: Int | None = None) -> Bytes:
        if size is None:
            return Bytes(self._impl.read())
        return Bytes(self._impl.read(size._value))

    def readline(self, size: Int | None = None) -> Bytes:
        if size is None:
            return Bytes(self._impl.readline())
        return Bytes(self._impl.readline(size._value))

    def write(self, data: Bytes) -> Int:
        return Int(self._impl.write(data._value))

    def getvalue(self) -> Bytes:
        return Bytes(self._impl.getvalue())

    def seek(self, pos: Int, whence: Int | None = None) -> Int:
        w = 0 if whence is None else whence._value
        return Int(self._impl.seek(pos._value, w))

    def tell(self) -> Int:
        return Int(self._impl.tell())

    def truncate(self, size: Int | None = None) -> Int:
        s = None if size is None else size._value
        return Int(self._impl.truncate(s))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.close()


class IO:
    """Namespace mirroring Python's `io` module — in-memory I/O."""

    StringIO: ClassVar[type[StringIO]] = StringIO
    BytesIO: ClassVar[type[BytesIO]] = BytesIO

    # Seek constants
    SEEK_SET: ClassVar[Int] = Int(_io.SEEK_SET)
    SEEK_CUR: ClassVar[Int] = Int(_io.SEEK_CUR)
    SEEK_END: ClassVar[Int] = Int(_io.SEEK_END)
    DEFAULT_BUFFER_SIZE: ClassVar[Int] = Int(_io.DEFAULT_BUFFER_SIZE)

    # Errors
    UnsupportedOperation: ClassVar[type[BaseException]] = _io.UnsupportedOperation
    BlockingIOError: ClassVar[type[BaseException]] = _io.BlockingIOError
