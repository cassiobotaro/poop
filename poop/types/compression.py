from typing import ClassVar

from poop.types.bz2 import Bz2
from poop.types.gzip import Gzip
from poop.types.lzma import Lzma
from poop.types.zlib import Zlib


class Compression:
    """Namespace mirroring Python 3.14's `compression` umbrella package.

    Each attribute aliases the same singleton as the standalone
    lowercase namespace (`zlib`, `gzip`, `bz2`, `lzma`), so callers
    can write either `gzip.compress(...)` or `compression.gzip.compress(...)`.

    `compression.zstd` is out of scope for v1 until Python 3.14's
    zstandard API stabilises.
    """

    zlib: ClassVar[type[Zlib]] = Zlib
    gzip: ClassVar[type[Gzip]] = Gzip
    bz2: ClassVar[type[Bz2]] = Bz2
    lzma: ClassVar[type[Lzma]] = Lzma
