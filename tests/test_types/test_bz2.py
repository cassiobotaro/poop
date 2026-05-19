from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.bytes import Bytes
from poop.types.bz2 import Bz2, BZ2Compressor, BZ2Decompressor, BZ2File
from poop.types.int import Int
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str

# --- Compress / Decompress ---


def test_compress_decompress_round_trip() -> None:
    data = Bytes(b"abc" * 200)
    compressed = Bz2.compress(data)
    assert isinstance(compressed, Bytes)
    assert Bz2.decompress(compressed) == data


def test_compress_with_level() -> None:
    data = Bytes(b"x" * 100)
    compressed = Bz2.compress(data, compresslevel=Int(1))
    assert Bz2.decompress(compressed) == data


# --- Streaming ---


def test_bz2_compressor_streaming() -> None:
    c = BZ2Compressor()
    parts = [c.compress(Bytes(b"alpha")), c.compress(Bytes(b"beta")), c.flush()]
    combined = b"".join(p._value for p in parts)
    assert Bz2.decompress(Bytes(combined)) == Bytes(b"alphabeta")


def test_bz2_decompressor_streaming() -> None:
    compressed = Bz2.compress(Bytes(b"chunked"))
    d = BZ2Decompressor()
    assert d.decompress(compressed) == Bytes(b"chunked")
    assert d.eof is true


def test_bz2_decompressor_state() -> None:
    d = BZ2Decompressor()
    assert d.needs_input is true
    assert isinstance(d.unused_data, Bytes)


def test_bz2_decompressor_max_length() -> None:
    compressed = Bz2.compress(Bytes(b"abc" * 50))
    d = BZ2Decompressor()
    chunk = d.decompress(compressed, max_length=Int(3))
    assert len(chunk._value) <= 3


# --- BZ2File ---


def test_bz2_open_write_read_round_trip(tmp_path: _PyPath) -> None:
    target = tmp_path / "out.bz2"
    f = Bz2.open(Path(Str(str(target))), mode=Str("wb"))
    assert isinstance(f, BZ2File)
    f.write(Bytes(b"payload"))
    f.close()
    reader = Bz2.open(Path(Str(str(target))))
    assert reader.read() == Bytes(b"payload")
    reader.close()


def test_bz2file_context_manager(tmp_path: _PyPath) -> None:
    target = tmp_path / "ctx.bz2"
    with Bz2.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"hello"))
    with Bz2.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.read() == Bytes(b"hello")


def test_bz2file_flush_returns_none(tmp_path: _PyPath) -> None:
    target = tmp_path / "flush.bz2"
    f = Bz2.open(Path(Str(str(target))), mode=Str("wb"))
    f.write(Bytes(b"x"))
    assert f.flush() is none
    f.close()


def test_bz2file_seek_tell(tmp_path: _PyPath) -> None:
    target = tmp_path / "seek.bz2"
    with Bz2.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"abcdef"))
    with Bz2.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.seek(Int(2)) == Int(2)
        assert f.tell() == Int(2)


# --- Interpreter integration ---


def test_bz2_compress_reachable_via_interpreter() -> None:
    Interpreter().run_source('bz2.compress(b"hello").len().print()')


def test_BZ2Compressor_reachable_via_interpreter() -> None:
    Interpreter().run_source('c = BZ2Compressor()\nc.compress(b"x").len().print()')
