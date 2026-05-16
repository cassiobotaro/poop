import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.zlib import Compress, Decompress, Zlib

# --- Round trip ---


def test_compress_decompress_round_trip() -> None:
    data = Bytes(b"hello world" * 50)
    compressed = Zlib.compress(data)
    assert isinstance(compressed, Bytes)
    restored = Zlib.decompress(compressed)
    assert restored == data


def test_compress_with_level() -> None:
    data = Bytes(b"abc" * 100)
    fast = Zlib.compress(data, level=Zlib.Z_BEST_SPEED)
    best = Zlib.compress(data, level=Zlib.Z_BEST_COMPRESSION)
    assert Zlib.decompress(fast) == data
    assert Zlib.decompress(best) == data


def test_decompress_invalid_raises() -> None:
    with pytest.raises(Zlib.error):
        Zlib.decompress(Bytes(b"not zlib data"))


# --- Streaming Compress / Decompress ---


def test_compressobj_streaming() -> None:
    co = Zlib.compressobj()
    parts = [co.compress(Bytes(b"alpha")), co.compress(Bytes(b"beta")), co.flush()]
    combined = b"".join(p._value for p in parts)
    assert Zlib.decompress(Bytes(combined)) == Bytes(b"alphabeta")


def test_decompressobj_streaming() -> None:
    compressed = Zlib.compress(Bytes(b"chunked data"))
    do = Zlib.decompressobj()
    out = do.decompress(compressed)
    out_value = out._value + do.flush()._value
    assert out_value == b"chunked data"


def test_compressobj_copy() -> None:
    co = Zlib.compressobj()
    co.compress(Bytes(b"prefix"))
    snapshot = co.copy()
    assert isinstance(snapshot, Compress)


def test_decompressobj_copy() -> None:
    compressed = Zlib.compress(Bytes(b"foo"))
    do = Zlib.decompressobj()
    do.decompress(compressed)
    snapshot = do.copy()
    assert isinstance(snapshot, Decompress)


def test_decompressobj_eof_and_unused_data() -> None:
    compressed = Zlib.compress(Bytes(b"x"))
    do = Zlib.decompressobj()
    do.decompress(compressed)
    do.flush()
    assert do.eof is True
    assert isinstance(do.unused_data, Bytes)
    assert isinstance(do.unconsumed_tail, Bytes)


def test_decompressobj_max_length() -> None:
    compressed = Zlib.compress(Bytes(b"abc" * 100))
    do = Zlib.decompressobj()
    chunk = do.decompress(compressed, max_length=Int(5))
    assert len(chunk._value) <= 5


def test_compress_flush_modes() -> None:
    co = Zlib.compressobj()
    co.compress(Bytes(b"data"))
    partial = co.flush(Zlib.Z_SYNC_FLUSH)
    assert isinstance(partial, Bytes)


# --- Checksums ---


def test_crc32_returns_int() -> None:
    result = Zlib.crc32(Bytes(b"abc"))
    assert isinstance(result, Int)
    assert result._value > 0


def test_crc32_with_seed() -> None:
    a = Zlib.crc32(Bytes(b"abc"))
    b = Zlib.crc32(Bytes(b"def"), value=a)
    assert isinstance(b, Int)
    assert b != a


def test_adler32_returns_int() -> None:
    result = Zlib.adler32(Bytes(b"abc"))
    assert isinstance(result, Int)
    assert result._value > 0


def test_adler32_with_seed() -> None:
    a = Zlib.adler32(Bytes(b"abc"))
    b = Zlib.adler32(Bytes(b"def"), value=a)
    assert b != a


# --- Constants ---


def test_constants_are_ints() -> None:
    assert isinstance(Zlib.MAX_WBITS, Int)
    assert isinstance(Zlib.Z_BEST_COMPRESSION, Int)
    assert isinstance(Zlib.Z_BEST_SPEED, Int)
    assert isinstance(Zlib.Z_DEFAULT_COMPRESSION, Int)
    assert isinstance(Zlib.Z_FILTERED, Int)
    assert isinstance(Zlib.Z_HUFFMAN_ONLY, Int)
    assert isinstance(Zlib.DEFLATED, Int)


def test_error_class_exposed() -> None:
    assert isinstance(Zlib.error, type)


# --- Interpreter integration ---


def test_zlib_compress_reachable_via_interpreter() -> None:
    Interpreter().run_source('zlib.compress(b"hello").len().print()')


def test_zlib_crc32_reachable_via_interpreter() -> None:
    Interpreter().run_source('zlib.crc32(b"abc").print()')


def test_Compress_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('co = zlib.compressobj()\nco.compress(b"x").len().print()')
