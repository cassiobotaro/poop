from __future__ import annotations

import zlib as _zlib
from typing import Any, ClassVar

from poop.types._unwrap import _opt_int
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.object import Object


class Compress(Object):
    """Wraps Python's `zlib.compressobj` — incremental compressor.

    `compress(data)` consumes a chunk and returns whatever output is
    ready; `flush(mode=Z_FINISH)` drains the trailing bytes. `.copy()`
    snapshots the compressor mid-stream.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def compress(self, data: Bytes) -> Bytes:
        return Bytes(self._impl.compress(data._value))

    def flush(self, mode: Int | None = None) -> Bytes:
        if mode is None:
            return Bytes(self._impl.flush())
        return Bytes(self._impl.flush(mode._value))

    def copy(self) -> Compress:
        return Compress(self._impl.copy())


class Decompress(Object):
    """Wraps Python's `zlib.decompressobj` — incremental decompressor.

    `decompress(data, max_length=none)` consumes a compressed chunk
    and emits whatever plain bytes are ready; `flush(length=none)`
    drains the rest. `.copy()` snapshots mid-stream; `.unused_data`
    and `.unconsumed_tail` expose the streaming cursor state.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def decompress(self, data: Bytes, max_length: Int | None = None) -> Bytes:
        if max_length is None:
            return Bytes(self._impl.decompress(data._value))
        return Bytes(self._impl.decompress(data._value, max_length._value))

    def flush(self, length: Int | None = None) -> Bytes:
        if length is None:
            return Bytes(self._impl.flush())
        return Bytes(self._impl.flush(length._value))

    def copy(self) -> Decompress:
        return Decompress(self._impl.copy())

    @property
    def unused_data(self) -> Bytes:
        return Bytes(self._impl.unused_data)

    @property
    def unconsumed_tail(self) -> Bytes:
        return Bytes(self._impl.unconsumed_tail)

    @property
    def eof(self) -> bool:
        return self._impl.eof


class Zlib:
    """Namespace mirroring Python's `zlib` module — DEFLATE compression
    plus CRC32/Adler32 checksums.

    One-shot `compress` / `decompress` for small buffers; streaming
    via `compressobj` / `decompressobj`. `zlib.error` is exposed for
    `Try.except_`.
    """

    error: ClassVar[type[Exception]] = _zlib.error

    # Compression-level constants.
    Z_DEFAULT_COMPRESSION: ClassVar[Int] = Int(_zlib.Z_DEFAULT_COMPRESSION)
    Z_BEST_SPEED: ClassVar[Int] = Int(_zlib.Z_BEST_SPEED)
    Z_BEST_COMPRESSION: ClassVar[Int] = Int(_zlib.Z_BEST_COMPRESSION)
    Z_NO_COMPRESSION: ClassVar[Int] = Int(_zlib.Z_NO_COMPRESSION)

    # Strategy constants.
    Z_DEFAULT_STRATEGY: ClassVar[Int] = Int(_zlib.Z_DEFAULT_STRATEGY)
    Z_FILTERED: ClassVar[Int] = Int(_zlib.Z_FILTERED)
    Z_HUFFMAN_ONLY: ClassVar[Int] = Int(_zlib.Z_HUFFMAN_ONLY)
    Z_RLE: ClassVar[Int] = Int(_zlib.Z_RLE)
    Z_FIXED: ClassVar[Int] = Int(_zlib.Z_FIXED)

    # Flush mode constants.
    Z_NO_FLUSH: ClassVar[Int] = Int(_zlib.Z_NO_FLUSH)
    Z_PARTIAL_FLUSH: ClassVar[Int] = Int(_zlib.Z_PARTIAL_FLUSH)
    Z_SYNC_FLUSH: ClassVar[Int] = Int(_zlib.Z_SYNC_FLUSH)
    Z_FULL_FLUSH: ClassVar[Int] = Int(_zlib.Z_FULL_FLUSH)
    Z_FINISH: ClassVar[Int] = Int(_zlib.Z_FINISH)
    Z_BLOCK: ClassVar[Int] = Int(_zlib.Z_BLOCK)
    Z_TREES: ClassVar[Int] = Int(_zlib.Z_TREES)

    # Window-bits / deflated.
    MAX_WBITS: ClassVar[Int] = Int(_zlib.MAX_WBITS)
    DEFLATED: ClassVar[Int] = Int(_zlib.DEFLATED)
    DEF_MEM_LEVEL: ClassVar[Int] = Int(_zlib.DEF_MEM_LEVEL)
    DEF_BUF_SIZE: ClassVar[Int] = Int(_zlib.DEF_BUF_SIZE)
    ZLIB_VERSION: ClassVar[Any] = _zlib.ZLIB_VERSION  # raw str (version banner)

    Compress: ClassVar[type[Compress]] = Compress
    Decompress: ClassVar[type[Decompress]] = Decompress

    @staticmethod
    def compress(
        data: Bytes,
        level: Int | None = None,
        wbits: Int | None = None,
    ) -> Bytes:
        return Bytes(
            _zlib.compress(
                data._value,
                _opt_int(level, _zlib.Z_DEFAULT_COMPRESSION),
                _opt_int(wbits, _zlib.MAX_WBITS),
            )
        )

    @staticmethod
    def decompress(
        data: Bytes,
        wbits: Int | None = None,
        bufsize: Int | None = None,
    ) -> Bytes:
        return Bytes(
            _zlib.decompress(
                data._value,
                _opt_int(wbits, _zlib.MAX_WBITS),
                _opt_int(bufsize, _zlib.DEF_BUF_SIZE),
            )
        )

    @staticmethod
    def compressobj(
        level: Int | None = None,
        method: Int | None = None,
        wbits: Int | None = None,
        memLevel: Int | None = None,
        strategy: Int | None = None,
        zdict: Bytes | None = None,
    ) -> Compress:
        kwargs: dict[str, Any] = {}
        if zdict is not None:
            kwargs["zdict"] = zdict._value
        return Compress(
            _zlib.compressobj(
                _opt_int(level, _zlib.Z_DEFAULT_COMPRESSION),
                _opt_int(method, _zlib.DEFLATED),
                _opt_int(wbits, _zlib.MAX_WBITS),
                _opt_int(memLevel, _zlib.DEF_MEM_LEVEL),
                _opt_int(strategy, _zlib.Z_DEFAULT_STRATEGY),
                **kwargs,
            )
        )

    @staticmethod
    def decompressobj(
        wbits: Int | None = None, zdict: Bytes | None = None
    ) -> Decompress:
        kwargs: dict[str, Any] = {}
        if zdict is not None:
            kwargs["zdict"] = zdict._value
        return Decompress(
            _zlib.decompressobj(_opt_int(wbits, _zlib.MAX_WBITS), **kwargs)
        )

    @staticmethod
    def adler32(data: Bytes, value: Int | None = None) -> Int:
        return Int(_zlib.adler32(data._value, _opt_int(value, 1)))

    @staticmethod
    def crc32(data: Bytes, value: Int | None = None) -> Int:
        return Int(_zlib.crc32(data._value, _opt_int(value, 0)))
