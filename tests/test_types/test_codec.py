"""`encode`/`decode` name the surface POOP supports instead of inheriting it.

CPython's failure advertised `codecs.encode()` — a module POOP has no `import`
to reach, so the advice sent the reader somewhere the language cannot go.
"""

from collections.abc import Callable
from typing import Any

import pytest

from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
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


# --- the argument's kind, before its value ---
#
# The table is read by lowercasing the argument, so a non-text one answered
# `'int' object has no attribute 'lower'`: the wrapper naming the Python
# method it happens to call, one guard short of the family in `_argument.py`.


@pytest.mark.parametrize(
    ("send", "selector"),
    [
        pytest.param(lambda arg: Str("abc").encode(arg), "encode", id="str"),
        pytest.param(lambda arg: Bytes(b"ab").decode(arg), "decode", id="bytes"),
        pytest.param(
            lambda arg: ByteArray(bytearray(b"ab")).decode(arg),
            "decode",
            id="bytearray",
        ),
    ],
)
def test_a_non_text_encoding_is_refused_by_its_kind(
    send: Callable[[Any], object], selector: str
) -> None:
    with pytest.raises(TypeError, match=f"^#{selector} expects a str, got an int$"):
        send(Int(1))


def test_a_bytes_encoding_is_refused_too() -> None:
    # `kinds=(str,)`: accepting `b"utf-8"` here would only move the refusal
    # into the branch that reports an unknown *value*.
    with pytest.raises(TypeError, match="^#encode expects a str, got a bytes$"):
        Str("abc").encode(Bytes(b"utf-8"))  # ty: ignore[invalid-argument-type]


def test_a_non_text_error_handler_is_refused_by_its_kind() -> None:
    # A ValueError about `1` said the handler was unknown, which describes a
    # wrong-typed argument as a wrong-valued one.
    with pytest.raises(TypeError, match="^#encode expects a str, got an int$"):
        Str("abc").encode(Str("utf-8"), Int(1))  # ty: ignore[invalid-argument-type]


def test_the_value_refusals_still_answer_a_value_error() -> None:
    with pytest.raises(ValueError, match="unknown encoding 'rot13'"):
        Str("a").encode(Str("rot13"))
    with pytest.raises(ValueError, match="unknown error handler 'namereplace'"):
        Str("a").encode(Str("utf-8"), Str("namereplace"))
