"""`encode`/`decode` name the surface POOP supports instead of inheriting it.

CPython's failure advertised `codecs.encode()` — a module POOP has no `import`
to reach, so the advice sent the reader somewhere the language cannot go.
"""

import pytest

from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.string import Str

_ENCODINGS = [
    "utf-8",
    "utf8",
    "UTF-8",
    "utf-16",
    "latin-1",
    "latin1",
    "iso-8859-1",
    "ascii",
    "us-ascii",
    "UTF_8",
]


@pytest.mark.parametrize("encoding", _ENCODINGS)
def test_accepted_encodings_round_trip(encoding: str) -> None:
    encoded = Str("abc").encode(Str(encoding))
    assert isinstance(encoded, Bytes)
    assert encoded.decode(Str(encoding)) == Str("abc")


@pytest.mark.parametrize(("handler", "expected"), [("ignore", b""), ("replace", b"?")])
def test_accepted_error_handlers_reach_the_codec(handler: str, expected: bytes) -> None:
    assert Str("é").encode(Str("ascii"), Str(handler)) == Bytes(expected)


def test_strict_is_the_default_handler() -> None:
    with pytest.raises(UnicodeEncodeError):
        Str("é").encode(Str("ascii"))


def test_an_unknown_encoding_does_not_point_at_the_codecs_module() -> None:
    with pytest.raises(ValueError, match=r"^unknown encoding 'rot13' — POOP encodes "):
        Str("a").encode(Str("rot13"))


def test_a_real_but_unsupported_encoding_is_refused_too() -> None:
    # The point is the named surface, not just the non-codecs ones: `cp1252`
    # is a text encoding CPython has and POOP does not offer.
    with pytest.raises(ValueError, match="unknown encoding 'cp1252'"):
        Bytes(b"a").decode(Str("cp1252"))


def test_an_unknown_error_handler_is_refused() -> None:
    # `namereplace` and `backslashreplace` are the same codec machinery under
    # another argument.
    with pytest.raises(ValueError, match=r"^unknown error handler 'namereplace' — "):
        Str("é").encode(Str("ascii"), Str("namereplace"))


def test_byte_array_decode_is_guarded_too() -> None:
    with pytest.raises(ValueError, match="unknown encoding 'rot13'"):
        ByteArray(bytearray(b"a")).decode(Str("rot13"))


def test_the_default_encoding_is_still_utf_8() -> None:
    assert Str("é").encode() == Bytes("é".encode())
