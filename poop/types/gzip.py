from __future__ import annotations

import gzip as _gzip
from types import TracebackType
from typing import ClassVar, Self

from poop.types._unwrap import _opt_int
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


class GzipFile(Object):
    """Wraps Python's `gzip.GzipFile` — a streaming gzip file handle.

    Construction is path-based (`GzipFile(path, mode='rb',
    compresslevel=9)`) per POOP's file-I/O convention. `With`-friendly;
    `.read` / `.write` use `Bytes`.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        path: Path | Str,
        mode: Str | None = None,
        compresslevel: Int | None = None,
    ) -> None:
        # CPython's gzip default compresslevel is 9 (best).
        self._impl = _gzip.GzipFile(
            _path_str(path),
            "rb" if mode is None else mode._value,
            _opt_int(compresslevel, 9),
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


class Gzip:
    """Namespace mirroring Python's `gzip` module — RFC 1952 gzip
    compression.

    `compress` / `decompress` are one-shot helpers; `open` returns a
    `GzipFile` (path-based; POOP has no file-object abstraction). The
    `BadGzipFile` exception class is exposed for `Try.except_`.
    """

    BadGzipFile: ClassVar[type[Exception]] = _gzip.BadGzipFile
    GzipFile: ClassVar[type[GzipFile]] = GzipFile

    @staticmethod
    def compress(
        data: Bytes, compresslevel: Int = Int(9), *, mtime: Int = Int(0)
    ) -> Bytes:
        return Bytes(
            _gzip.compress(data._value, compresslevel._value, mtime=mtime._value)
        )

    @staticmethod
    def decompress(data: Bytes) -> Bytes:
        return Bytes(_gzip.decompress(data._value))

    @staticmethod
    def open(
        filename: Path | Str,
        mode: Str = Str("rb"),
        compresslevel: Int = Int(9),
        encoding: Str | None = None,
        errors: Str | None = None,
        newline: Str | None = None,
    ) -> GzipFile:
        # `encoding`/`errors`/`newline` exposed for signature parity;
        # POOP's GzipFile is byte-mode only.
        if encoding is not None or errors is not None or newline is not None:
            raise ValueError(
                "encoding/errors/newline require text mode; POOP GzipFile is byte-mode only"
            )
        return GzipFile(filename, mode, compresslevel)
