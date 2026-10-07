from functools import partial

import pytest

from poop.transformers.bytes import BytesTransformer, _poop_bytes_from
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, BytesTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = b'hello'", "x = _poop_bytes(b'hello')"),
        ("bytes(x)", "_poop_bytes_from(x)"),
        ('bytes(x, "utf-8")', "_poop_bytes_from(x, 'utf-8')"),
        ("x.bytes()", "x.bytes()"),
    ],
    ids=["literal", "call", "call_with_encoding", "method_named_bytes"],
)
def test_bytes_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_bytes_class() -> None:
    assert BytesTransformer.BINDINGS["_poop_bytes"] is Bytes


def test_bindings_contains_bytes_from_factory() -> None:
    assert BytesTransformer.BINDINGS["_poop_bytes_from"] is _poop_bytes_from


# _poop_bytes_from factory tests


def test_bytes_from_no_arg_returns_empty() -> None:
    result = _poop_bytes_from()
    assert isinstance(result, Bytes)
    assert result._value == b""


def test_bytes_from_bytes_returns_same() -> None:
    x = Bytes(b"hello")
    assert _poop_bytes_from(x) is x


def test_bytes_from_int_returns_zero_filled() -> None:
    result = _poop_bytes_from(Int(3))
    assert isinstance(result, Bytes)
    assert result._value == b"\x00\x00\x00"


def test_bytes_from_str_requires_an_encoding() -> None:
    # It used to invent utf-8, which is the one thing a converter between text
    # and bytes must not do quietly: without an encoding there is no answer to
    # give, only a guess about what the text means as bytes. CPython refuses
    # for the same reason, in the same words.
    with pytest.raises(TypeError, match="string argument without an encoding"):
        _poop_bytes_from(Str("hello"))


def test_bytes_refuses_an_encoding_without_text() -> None:
    with pytest.raises(TypeError, match="encoding without a string argument"):
        _poop_bytes_from(Bytes(b"ab"), Str("utf-8"))


def test_bytes_from_str_routes_the_encoding_through_the_codec_surface() -> None:
    # `_codec.py` exists to keep `'rot13' is not a text encoding; use
    # codecs.encode() ...` out of the language — advice pointing at a module
    # `no_import` forbids. The converter reached into `_value` and called
    # `str.encode` itself, so it was the one encoding argument that never saw
    # the guard; a wrong-*typed* one was ignored outright.
    with pytest.raises(ValueError, match="unknown encoding 'rot13'"):
        _poop_bytes_from(Str("ab"), Str("rot13"))
    with pytest.raises(TypeError, match="#encode expects a str, got an int"):
        _poop_bytes_from(Str("ab"), Int(5))
    with pytest.raises(ValueError, match="ascii cannot encode 'é' at position 0"):
        _poop_bytes_from(Str("é"), Str("ascii"))


def test_bytes_from_str_takes_the_errors_handler_too() -> None:
    result = _poop_bytes_from(Str("aéb"), Str("ascii"), Str("ignore"))
    assert isinstance(result, Bytes)
    assert result._value == b"ab"


def test_bytes_from_str_with_explicit_encoding() -> None:
    result = _poop_bytes_from(Str("hello"), Str("ascii"))
    assert isinstance(result, Bytes)
    assert result._value == b"hello"


def test_bytes_from_list_of_ints() -> None:
    result = _poop_bytes_from(List(Int(72), Int(101), Int(108)))
    assert isinstance(result, Bytes)
    assert result._value == b"Hel"


def test_bytes_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_bytes_from(Float(3.14))


def test_bare_bytes_name_is_rewritten_to_the_mangled_binding() -> None:
    assert _rewritten("f = bytes") == "f = _poop_bytes_cls"
