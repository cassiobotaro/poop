from functools import partial

import pytest

from poop.transformers.string import StrTransformer, _poop_str_from
from poop.types.boolean import false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, StrTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('x = "hello"', "x = _poop_str('hello')"),
        ("x = 42", "x = 42"),
        ("str(x)", "_poop_str_from(x)"),
        # `str(b"x", encoding=...)` is a valid CPython call answering `"x"`.
        # It used to fall through to the class rename, which answered
        # `str.__init__() takes 2 positional arguments but 3 were given` — a
        # dunder the program never wrote. The keyword is preserved, not dropped.
        (
            'str(b"x", encoding="utf-8")',
            "_poop_str_from(b'x', encoding=_poop_str('utf-8'))",
        ),
        ('str(b"x", "utf-8")', "_poop_str_from(b'x', _poop_str('utf-8'))"),
        ("x.str()", "x.str()"),
    ],
    ids=[
        "literal",
        "int_literal_not_rewritten",
        "call",
        "call_with_keyword_reaches_the_converter",
        "call_with_two_positional_args_reaches_the_converter",
        "method_named_str",
    ],
)
def test_str_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_str_class() -> None:
    assert StrTransformer.BINDINGS["_poop_str"] is Str


def test_bindings_contains_str_from_factory() -> None:
    assert StrTransformer.BINDINGS["_poop_str_from"] is _poop_str_from


# _poop_str_from factory tests


def test_str_from_no_arg_returns_empty_str() -> None:
    result = _poop_str_from()
    assert isinstance(result, Str)
    assert result._value == ""


def test_str_from_str_returns_same() -> None:
    x = Str("hello")
    assert _poop_str_from(x) is x


def test_str_from_int_converts() -> None:
    result = _poop_str_from(Int(42))
    assert isinstance(result, Str)
    assert result._value == "42"


def test_str_from_float_converts() -> None:
    result = _poop_str_from(Float(3.14))
    assert isinstance(result, Str)
    assert result._value == "3.14"


def test_str_from_bool_converts() -> None:
    assert _poop_str_from(true)._value == "True"
    assert _poop_str_from(false)._value == "False"


# the decoding form, and the refusals around it


def test_str_from_bytes_and_encoding_decodes() -> None:
    assert _poop_str_from(Bytes(b"ab"), Str("utf-8")) == Str("ab")
    assert _poop_str_from(Bytes(b"ab"), encoding=Str("utf-8")) == Str("ab")
    assert _poop_str_from(ByteArray(bytearray(b"ab")), Str("utf-8"), Str("strict")) == (
        Str("ab")
    )


def test_str_decoding_form_needs_bytes() -> None:
    with pytest.raises(TypeError, match="decoding needs bytes, got int"):
        _poop_str_from(Int(5), Str("utf-8"))


def test_str_refuses_a_fourth_argument() -> None:
    with pytest.raises(TypeError, match="str is built from one value"):
        _poop_str_from(Int(1), Int(2), Int(3), Int(4))


def test_str_refuses_an_unknown_keyword() -> None:
    with pytest.raises(TypeError, match="no keyword argument 'zap'"):
        _poop_str_from(Int(1), zap=Int(2))


def test_str_refuses_a_slot_given_twice() -> None:
    with pytest.raises(TypeError, match="given 'object' twice"):
        _poop_str_from(Int(1), object=Int(2))
