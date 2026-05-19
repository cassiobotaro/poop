from __future__ import annotations

import lzma as _lzma
from types import TracebackType
from typing import ClassVar, Self

from poop.types._unwrap import _kwargs_from
from poop.types.boolean import Boolean, false, true
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


class LZMACompressor(Object):
    """Wraps Python's `lzma.LZMACompressor` — incremental LZMA compressor.

    Construction takes the same keyword tuning as upstream
    (`format=FORMAT_XZ`, `check=-1`, `preset=none`, `filters=none`).
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        format: Int | None = None,
        check: Int | None = None,
        preset: Int | None = None,
    ) -> None:
        kwargs = _kwargs_from(format=format, check=check, preset=preset)
        self._impl = _lzma.LZMACompressor(**kwargs)

    def compress(self, data: Bytes) -> Bytes:
        return Bytes(self._impl.compress(data._value))

    def flush(self) -> Bytes:
        return Bytes(self._impl.flush())


class LZMADecompressor(Object):
    """Wraps Python's `lzma.LZMADecompressor` — incremental decompressor."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        format: Int | None = None,
        memlimit: Int | None = None,
    ) -> None:
        kwargs = _kwargs_from(format=format, memlimit=memlimit)
        self._impl = _lzma.LZMADecompressor(**kwargs)

    def decompress(self, data: Bytes, max_length: Int | None = None) -> Bytes:
        if max_length is None:
            return Bytes(self._impl.decompress(data._value))
        return Bytes(self._impl.decompress(data._value, max_length._value))

    @property
    def eof(self) -> Boolean:
        return true if self._impl.eof else false

    @property
    def needs_input(self) -> Boolean:
        return true if self._impl.needs_input else false

    @property
    def unused_data(self) -> Bytes:
        return Bytes(self._impl.unused_data)

    @property
    def check(self) -> Int:
        return Int(self._impl.check)


class LZMAFile(Object):
    """Wraps Python's `lzma.LZMAFile` — path-based LZMA/XZ file handle.

    `With`-friendly; `.read` / `.write` use `Bytes`.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        path: Path | Str,
        mode: Str | NoneClass | None = None,
        format: Int | None = None,
        check: Int | NoneClass | None = None,
        preset: Int | None = None,
    ) -> None:
        from poop.types._unwrap import _is_absent

        kwargs = _kwargs_from(format=format, check=check, preset=preset)
        self._impl = _lzma.LZMAFile(
            _path_str(path),
            "rb" if _is_absent(mode) else mode._value,  # ty: ignore[unresolved-attribute]
            **kwargs,
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


class Lzma:
    """Namespace mirroring Python's `lzma` module — LZMA/XZ compression."""

    # Format constants.
    FORMAT_XZ: ClassVar[Int] = Int(_lzma.FORMAT_XZ)
    FORMAT_ALONE: ClassVar[Int] = Int(_lzma.FORMAT_ALONE)
    FORMAT_RAW: ClassVar[Int] = Int(_lzma.FORMAT_RAW)
    FORMAT_AUTO: ClassVar[Int] = Int(_lzma.FORMAT_AUTO)

    # Integrity-check constants.
    CHECK_NONE: ClassVar[Int] = Int(_lzma.CHECK_NONE)
    CHECK_CRC32: ClassVar[Int] = Int(_lzma.CHECK_CRC32)
    CHECK_CRC64: ClassVar[Int] = Int(_lzma.CHECK_CRC64)
    CHECK_SHA256: ClassVar[Int] = Int(_lzma.CHECK_SHA256)
    CHECK_ID_MAX: ClassVar[Int] = Int(_lzma.CHECK_ID_MAX)
    CHECK_UNKNOWN: ClassVar[Int] = Int(_lzma.CHECK_UNKNOWN)

    # Preset constants.
    PRESET_DEFAULT: ClassVar[Int] = Int(_lzma.PRESET_DEFAULT)
    PRESET_EXTREME: ClassVar[Int] = Int(_lzma.PRESET_EXTREME)

    LZMAError: ClassVar[type[Exception]] = _lzma.LZMAError
    LZMACompressor: ClassVar[type[LZMACompressor]] = LZMACompressor
    LZMADecompressor: ClassVar[type[LZMADecompressor]] = LZMADecompressor
    LZMAFile: ClassVar[type[LZMAFile]] = LZMAFile

    @staticmethod
    def compress(
        data: Bytes,
        format: Int = Int(_lzma.FORMAT_XZ),
        check: Int = Int(-1),
        preset: Int | None = None,
    ) -> Bytes:
        if preset is None:
            return Bytes(
                _lzma.compress(data._value, format=format._value, check=check._value)
            )
        return Bytes(
            _lzma.compress(
                data._value,
                format=format._value,
                check=check._value,
                preset=preset._value,
            )
        )

    @staticmethod
    def decompress(
        data: Bytes,
        format: Int = Int(_lzma.FORMAT_AUTO),
        memlimit: Int | None = None,
    ) -> Bytes:
        if memlimit is None:
            return Bytes(_lzma.decompress(data._value, format=format._value))
        return Bytes(
            _lzma.decompress(
                data._value, format=format._value, memlimit=memlimit._value
            )
        )

    @staticmethod
    def open(
        filename: Path | Str,
        mode: Str | NoneClass | None = None,
        *,
        format: Int | None = None,
        check: Int | NoneClass | None = None,
        preset: Int | None = None,
        errors: Str | None = None,
        newline: Str | None = None,
        encoding: Str | None = None,
    ) -> LZMAFile:
        # `encoding`/`errors`/`newline` exposed for signature parity;
        # POOP's LZMAFile is byte-mode only.
        if encoding is not None or errors is not None or newline is not None:
            raise ValueError(
                "encoding/errors/newline require text mode; POOP LZMAFile is byte-mode only"
            )
        return LZMAFile(filename, mode, format, check, preset)

    @staticmethod
    def is_check_supported(check_id: Int, /) -> Boolean:
        return true if _lzma.is_check_supported(check_id._value) else false
