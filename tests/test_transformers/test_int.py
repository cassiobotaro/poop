from functools import partial

import pytest

from poop.transformers.int import IntTransformer, _poop_int_from
from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, IntTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = 42", "x = _poop_int(42)"),
        ("x = -1", "x = _poop_int(-1)"),
        ('int("42")', "_poop_int_from('42')"),
        ('int("ff", 16)', "_poop_int_from('ff', _poop_int(16))"),
    ],
    ids=["literal", "negative_literal_collapsed", "call", "call_with_base"],
)
def test_int_is_rewritten(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "x = True",
        "x = 'hello'",
        "x.int()",
        "x = -y",
        # `-3.14` is USub on a Constant, but the value is a float, not an int,
        # so the int rewriter leaves it for the float transformer instead of
        # wrapping it.
        "y = -3.14",
    ],
    ids=["bool", "str", "method_named_int", "negative_variable", "negative_float"],
)
def test_int_is_not_rewritten(source: str) -> None:
    assert _rewritten(source) == source


def test_bindings_contains_int_class() -> None:
    assert IntTransformer.BINDINGS["_poop_int"] is Int


def test_bindings_contains_int_from_factory() -> None:
    assert IntTransformer.BINDINGS["_poop_int_from"] is _poop_int_from


# _poop_int_from factory tests


def test_int_from_int_returns_same() -> None:
    x = Int(42)
    assert _poop_int_from(x) is x


def test_int_from_none_returns_zero() -> None:
    result = _poop_int_from()
    assert isinstance(result, Int)
    assert result._value == 0


def test_int_from_float_truncates() -> None:
    result = _poop_int_from(Float(3.9))
    assert isinstance(result, Int)
    assert result._value == 3


def test_int_from_str_parses() -> None:
    result = _poop_int_from(Str("42"))
    assert isinstance(result, Int)
    assert result._value == 42


def test_int_from_str_with_base() -> None:
    result = _poop_int_from(Str("ff"), Int(16))
    assert isinstance(result, Int)
    assert result._value == 255


def test_int_from_str_with_non_int_base_raises() -> None:
    with pytest.raises(TypeError, match="base must be int"):
        _poop_int_from(Str("10"), "invalid_base")


def test_int_from_non_string_with_base_raises() -> None:
    # CPython: int(10, 2) / int(3.5, 2) / int(True, 2) raise `int() can't
    # convert non-string with explicit base` — the builtin as a call, in a
    # message POOP composes itself. The base must not be silently dropped for
    # Int/Float/Boolean values.
    for value in (Int(10), Float(3.5), true):
        with pytest.raises(TypeError, match="a base applies only to text"):
            _poop_int_from(value, Int(2))


def test_int_from_boolean() -> None:
    # int(True) -> 1, int(False) -> 0.
    assert _poop_int_from(true) == Int(1)
    assert _poop_int_from(false) == Int(0)


def test_int_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_int_from(Complex(complex(1, 2)))


def test_int_from_error_uses_masked_name() -> None:
    # The diagnostic must show the public name, not internal class names.
    with pytest.raises(TypeError, match="cannot convert complex to int"):
        _poop_int_from(Complex(complex(1, 2)))


def test_int_from_an_unparsable_string_does_not_name_the_call() -> None:
    # `invalid literal for int() with base 10: 'abc'` describes a Python call
    # and an argument the reader did not pass.
    with pytest.raises(ValueError, match=r"^'abc' is not a valid int$"):
        _poop_int_from(Str("abc"))


def test_int_from_an_out_of_range_base_does_not_name_the_call() -> None:
    with pytest.raises(ValueError, match=r"^int base must be 0, or between 2 and 36$"):
        _poop_int_from(Str("ff"), Int(99))


def test_int_from_an_unparsable_string_states_the_base_when_given() -> None:
    with pytest.raises(ValueError, match=r"^'zz' is not a valid int in base 16$"):
        _poop_int_from(Str("zz"), Int(16))
