from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.lzma import Lzma, LZMACompressor, LZMADecompressor, LZMAFile
from poop.types.none import none
from poop.types.path import Path
from poop.types.string import Str

# --- Compress / Decompress ---


def test_compress_decompress_round_trip() -> None:
    data = Bytes(b"hello compression" * 50)
    compressed = Lzma.compress(data)
    assert isinstance(compressed, Bytes)
    assert Lzma.decompress(compressed) == data


def test_compress_with_format() -> None:
    data = Bytes(b"alpha" * 100)
    compressed = Lzma.compress(data, format=Lzma.FORMAT_XZ)
    assert Lzma.decompress(compressed, format=Lzma.FORMAT_XZ) == data


def test_compress_with_check() -> None:
    data = Bytes(b"check data")
    compressed = Lzma.compress(data, check=Lzma.CHECK_SHA256)
    assert Lzma.decompress(compressed) == data


def test_compress_with_preset() -> None:
    data = Bytes(b"preset data" * 50)
    compressed = Lzma.compress(data, preset=Int(0))
    assert Lzma.decompress(compressed) == data


# --- Streaming ---


def test_lzma_compressor_streaming() -> None:
    c = LZMACompressor()
    parts = [c.compress(Bytes(b"x" * 100)), c.flush()]
    combined = b"".join(p._value for p in parts)
    assert Lzma.decompress(Bytes(combined)) == Bytes(b"x" * 100)


def test_lzma_decompressor_streaming() -> None:
    compressed = Lzma.compress(Bytes(b"chunked"))
    d = LZMADecompressor()
    assert d.decompress(compressed) == Bytes(b"chunked")
    assert d.eof is True


def test_lzma_decompressor_state() -> None:
    d = LZMADecompressor()
    assert d.needs_input is True
    assert isinstance(d.unused_data, Bytes)
    assert isinstance(d.check, Int)


def test_lzma_decompressor_max_length() -> None:
    compressed = Lzma.compress(Bytes(b"xyz" * 100))
    d = LZMADecompressor()
    chunk = d.decompress(compressed, max_length=Int(3))
    assert len(chunk._value) <= 3


# --- LZMAFile ---


def test_lzma_open_write_read_round_trip(tmp_path: _PyPath) -> None:
    target = tmp_path / "out.xz"
    f = Lzma.open(Path(Str(str(target))), mode=Str("wb"))
    assert isinstance(f, LZMAFile)
    f.write(Bytes(b"payload"))
    f.close()
    reader = Lzma.open(Path(Str(str(target))))
    assert reader.read() == Bytes(b"payload")
    reader.close()


def test_lzmafile_context_manager(tmp_path: _PyPath) -> None:
    target = tmp_path / "ctx.xz"
    with Lzma.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"hi"))
    with Lzma.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.read() == Bytes(b"hi")


def test_lzmafile_flush_returns_none(tmp_path: _PyPath) -> None:
    target = tmp_path / "flush.xz"
    f = Lzma.open(Path(Str(str(target))), mode=Str("wb"))
    f.write(Bytes(b"x"))
    assert f.flush() is none
    f.close()


def test_lzmafile_seek_tell(tmp_path: _PyPath) -> None:
    target = tmp_path / "seek.xz"
    with Lzma.open(Path(Str(str(target))), mode=Str("wb")) as f:
        f.write(Bytes(b"abcdef"))
    with Lzma.open(Path(Str(str(target))), mode=Str("rb")) as f:
        assert f.seek(Int(2)) == Int(2)
        assert f.tell() == Int(2)


# --- Constants ---


def test_format_constants_are_ints() -> None:
    assert isinstance(Lzma.FORMAT_XZ, Int)
    assert isinstance(Lzma.FORMAT_ALONE, Int)
    assert isinstance(Lzma.FORMAT_RAW, Int)
    assert isinstance(Lzma.FORMAT_AUTO, Int)


def test_check_constants_are_ints() -> None:
    assert isinstance(Lzma.CHECK_NONE, Int)
    assert isinstance(Lzma.CHECK_CRC32, Int)
    assert isinstance(Lzma.CHECK_CRC64, Int)
    assert isinstance(Lzma.CHECK_SHA256, Int)


def test_preset_constants_are_ints() -> None:
    assert isinstance(Lzma.PRESET_DEFAULT, Int)
    assert isinstance(Lzma.PRESET_EXTREME, Int)


def test_is_check_supported() -> None:
    assert isinstance(Lzma.is_check_supported(Lzma.CHECK_NONE), bool)


# --- Extra coverage ---


def test_decompress_with_memlimit() -> None:
    data = Bytes(b"data" * 10)
    compressed = Lzma.compress(data)
    # Big enough memlimit to succeed.
    assert Lzma.decompress(compressed, memlimit=Int(1024 * 1024 * 10)) == data


def test_compressor_with_format_check_preset() -> None:
    c = LZMACompressor(
        format=Lzma.FORMAT_XZ,
        check=Lzma.CHECK_CRC64,
        preset=Int(0),
    )
    parts = [c.compress(Bytes(b"x" * 50)), c.flush()]
    combined = b"".join(p._value for p in parts)
    assert Lzma.decompress(Bytes(combined)) == Bytes(b"x" * 50)


def test_decompressor_with_format_memlimit() -> None:
    compressed = Lzma.compress(Bytes(b"hi"))
    d = LZMADecompressor(format=Lzma.FORMAT_XZ, memlimit=Int(1024 * 1024 * 64))
    assert d.decompress(compressed) == Bytes(b"hi")


def test_lzmafile_with_format_check_preset(tmp_path: _PyPath) -> None:
    target = tmp_path / "tuned.xz"
    f = Lzma.open(
        Path(Str(str(target))),
        mode=Str("wb"),
        format=Lzma.FORMAT_XZ,
        check=Lzma.CHECK_SHA256,
        preset=Int(1),
    )
    f.write(Bytes(b"hello"))
    f.close()
    with Lzma.open(Path(Str(str(target)))) as reader:
        assert reader.read() == Bytes(b"hello")


# --- Interpreter integration ---


def test_lzma_compress_reachable_via_interpreter() -> None:
    Interpreter().run_source('lzma.compress(b"hello").len().print()')


def test_LZMAFile_reachable_via_interpreter(tmp_path: _PyPath) -> None:
    target = tmp_path / "i.xz"
    Interpreter().run_source(
        f'f = lzma.open(Path("{target}"), "wb")\nf.write(b"hi")\nf.close()'
    )
    assert target.exists()
