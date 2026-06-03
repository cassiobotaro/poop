from __future__ import annotations

import bz2 as _bz2
from types import TracebackType
from typing import ClassVar, Self

from poop.types._unwrap import _opt_int
from poop.types.boolean import Boolean, to_boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


def _path_str(value: Path | Str) -> str:
    if isinstance(value, Path):
        return str(value._path)
    return value._value


class BZ2Compressor(Object):
    """Wraps Python's `bz2.BZ2Compressor` — incremental bzip2 compressor.

    `compress(data)` consumes a chunk; `flush()` drains the trailing
    bytes.
    """

    __slots__ = ("_impl",)

    def __init__(self, compresslevel: Int | None = None) -> None:
        self._impl = _bz2.BZ2Compressor(_opt_int(compresslevel, 9))

    def compress(self, data: Bytes) -> Bytes:
        return Bytes(self._impl.compress(data._value))

    def flush(self) -> Bytes:
        return Bytes(self._impl.flush())


class BZ2Decompressor(Object):
    """Wraps Python's `bz2.BZ2Decompressor` — incremental decompressor.

    `decompress(data, max_length=none)` consumes a compressed chunk;
    `.eof` / `.needs_input` / `.unused_data` expose stream state.
    """

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _bz2.BZ2Decompressor()

    def decompress(self, data: Bytes, max_length: Int | None = None) -> Bytes:
        if max_length is None:
            return Bytes(self._impl.decompress(data._value))
        return Bytes(self._impl.decompress(data._value, max_length._value))

    @property
    def eof(self) -> Boolean:
        return to_boolean(self._impl.eof)

    @property
    def needs_input(self) -> Boolean:
        return to_boolean(self._impl.needs_input)

    @property
    def unused_data(self) -> Bytes:
        return Bytes(self._impl.unused_data)


class BZ2File(Object):
    """Wraps Python's `bz2.BZ2File` — path-based bzip2 file handle.

    `With`-friendly; `.read` / `.write` use `Bytes`.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        path: Path | Str,
        mode: Str | NoneClass | None = None,
        compresslevel: Int | NoneClass | None = None,
    ) -> None:
        from poop.types._unwrap import _is_absent

        self._impl = _bz2.BZ2File(  # ty: ignore[no-matching-overload]
            _path_str(path),
            "rb" if _is_absent(mode) else mode._value,
            compresslevel=_opt_int(compresslevel, 9),
        )

    def read(self, size: Int | None = None) -> Bytes:
        if size is None:
            return Bytes(self._impl.read())
        return Bytes(self._impl.read(size._value))

    def write(self, data: Bytes) -> Int:
        return Int(self._impl.write(data._value))

    def seek(self, offset: Int, whence: Int | None = None) -> Int:
        if whence is None:
            return Int(self._impl.seek(offset._value))
        return Int(self._impl.seek(offset._value, whence._value))

    def tell(self) -> Int:
        return Int(self._impl.tell())

    def flush(self) -> NoneClass:
        self._impl.flush()
        return none

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        self._impl.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class Bz2:
    """Namespace mirroring Python's `bz2` module — bzip2 compression.

    One-shot `compress` / `decompress`; streaming via `BZ2Compressor` /
    `BZ2Decompressor`; path-based `open` returning `BZ2File`.
    """

    BZ2Compressor: ClassVar[type[BZ2Compressor]] = BZ2Compressor
    BZ2Decompressor: ClassVar[type[BZ2Decompressor]] = BZ2Decompressor
    BZ2File: ClassVar[type[BZ2File]] = BZ2File

    @staticmethod
    def compress(data: Bytes, compresslevel: Int | None = None) -> Bytes:
        return Bytes(_bz2.compress(data._value, _opt_int(compresslevel, 9)))

    @staticmethod
    def decompress(data: Bytes) -> Bytes:
        return Bytes(_bz2.decompress(data._value))

    @staticmethod
    def open(
        filename: Path | Str,
        mode: Str | NoneClass | None = None,
        compresslevel: Int | NoneClass | None = None,
        encoding: Str | None = None,
        errors: Str | None = None,
        newline: Str | None = None,
    ) -> BZ2File:
        # `encoding`/`errors`/`newline` are exposed for signature parity
        # with CPython; POOP's BZ2File is byte-mode-only, so any non-None
        # value here triggers the same error CPython raises when text
        # decoding is requested without 't' in the mode.
        if encoding is not None or errors is not None or newline is not None:
            raise ValueError(
                "encoding/errors/newline require text mode; POOP BZ2File is byte-mode only"
            )
        return BZ2File(filename, mode, compresslevel)
