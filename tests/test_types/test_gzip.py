from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.gzip import Gzip, GzipFile
from poop.types.int import Int
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str

# --- Compress / Decompress ---


def test_compress_decompress_round_trip() -> None:
    data = Bytes(b"hello world" * 50)
    compressed = Gzip.compress(data)
    assert isinstance(compressed, Bytes)
    assert Gzip.decompress(compressed) == data


def test_compress_with_level() -> None:
    data = Bytes(b"abc" * 100)
    fast = Gzip.compress(data, compresslevel=Int(1))
    best = Gzip.compress(data, compresslevel=Int(9))
    assert Gzip.decompress(fast) == data
    assert Gzip.decompress(best) == data


def test_decompress_invalid_raises() -> None:
    with pytest.raises(Gzip.BadGzipFile):
        Gzip.decompress(Bytes(b"not gzip data"))


# --- GzipFile ---


def test_gzip_open_write_read_round_trip(tmp_path: _PyPath) -> None:
    target = tmp_path / "out.gz"
    handle = Gzip.open(Path(Str(str(target))), mode=Str("wb"))
    assert isinstance(handle, GzipFile)
    handle.write(Bytes(b"payload"))
    handle.close()
    reader = Gzip.open(Path(Str(str(target))))
    assert reader.read() == Bytes(b"payload")
    reader.close()


def test_gzipfile_context_manager(tmp_path: _PyPath) -> None:
    target = tmp_path / "ctx.gz"
    with Gzip.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"hello"))
    with Gzip.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.read() == Bytes(b"hello")


def test_gzipfile_seek_tell(tmp_path: _PyPath) -> None:
    target = tmp_path / "seek.gz"
    with Gzip.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"abcdef"))
    with Gzip.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.seek(Int(3)) == Int(3)
        assert f.tell() == Int(3)
        assert f.read() == Bytes(b"def")


def test_gzipfile_flush_returns_none(tmp_path: _PyPath) -> None:
    target = tmp_path / "flush.gz"
    f = Gzip.open(Path(Str(str(target))), mode=Str("wb"))
    f.write(Bytes(b"x"))
    assert f.flush() is none
    f.close()


# --- Interpreter integration ---


def test_gzip_compress_reachable_via_interpreter() -> None:
    Interpreter().run_source('gzip.compress(b"hello").len().print()')


def test_GzipFile_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    target = tmp_path / "i.gz"
    Interpreter().run_source(
        f'f = gzip.open(Path("{target}"), "wb")\nf.write(b"hi")\nf.close()'
    )
    assert target.exists()
