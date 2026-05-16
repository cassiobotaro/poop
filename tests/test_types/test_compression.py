from poop.interpreter import Interpreter
from poop.types.bytes import Bytes
from poop.types.bz2 import Bz2
from poop.types.compression import Compression
from poop.types.gzip import Gzip
from poop.types.lzma import Lzma
from poop.types.zlib import Zlib


def test_umbrella_aliases_individual_namespaces() -> None:
    assert Compression.zlib is Zlib
    assert Compression.gzip is Gzip
    assert Compression.bz2 is Bz2
    assert Compression.lzma is Lzma


def test_umbrella_zlib_round_trip() -> None:
    data = Bytes(b"hello" * 50)
    compressed = Compression.zlib.compress(data)
    assert Compression.zlib.decompress(compressed) == data


def test_umbrella_gzip_round_trip() -> None:
    data = Bytes(b"hello" * 50)
    compressed = Compression.gzip.compress(data)
    assert Compression.gzip.decompress(compressed) == data


def test_umbrella_bz2_round_trip() -> None:
    data = Bytes(b"hello" * 50)
    compressed = Compression.bz2.compress(data)
    assert Compression.bz2.decompress(compressed) == data


def test_umbrella_lzma_round_trip() -> None:
    data = Bytes(b"hello" * 50)
    compressed = Compression.lzma.compress(data)
    assert Compression.lzma.decompress(compressed) == data


# --- Interpreter integration ---


def test_compression_zlib_reachable_via_interpreter() -> None:
    Interpreter().run_source('compression.zlib.compress(b"x").len().print()')


def test_compression_gzip_reachable_via_interpreter() -> None:
    Interpreter().run_source('compression.gzip.compress(b"x").len().print()')


def test_compression_bz2_reachable_via_interpreter() -> None:
    Interpreter().run_source('compression.bz2.compress(b"x").len().print()')


def test_compression_lzma_reachable_via_interpreter() -> None:
    Interpreter().run_source('compression.lzma.compress(b"x").len().print()')
