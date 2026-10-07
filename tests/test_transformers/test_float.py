from functools import partial

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter
from poop.transformers.float import FloatTransformer, _poop_float_from
from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, FloatTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = 3.14", "x = _poop_float(3.14)"),
        ("x = -3.14", "x = _poop_float(-3.14)"),
        ('float("3.14")', "_poop_float_from('3.14')"),
    ],
    ids=["literal", "negative_literal_collapsed", "call"],
)
def test_float_is_rewritten(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "x = 42",
        "x = 'hello'",
        "x.float()",
        "x = -y",
        # `-5` is USub on a Constant, but the value is an int, not a float, so
        # the float rewriter leaves it for the int transformer instead of
        # wrapping it.
        "y = -5",
    ],
    ids=["int", "str", "method_named_float", "negative_variable", "negative_int"],
)
def test_float_is_not_rewritten(source: str) -> None:
    assert _rewritten(source) == source


def test_bindings_contains_float_class() -> None:
    assert FloatTransformer.BINDINGS["_poop_float"] is Float


def test_bindings_contains_float_from_factory() -> None:
    assert FloatTransformer.BINDINGS["_poop_float_from"] is _poop_float_from


# _poop_float_from factory tests


def test_float_from_float_returns_same() -> None:
    x = Float(3.14)
    assert _poop_float_from(x) is x


def test_float_from_none_returns_zero() -> None:
    result = _poop_float_from()
    assert isinstance(result, Float)
    assert result._value == pytest.approx(0.0)


def test_float_from_int_converts() -> None:
    result = _poop_float_from(Int(42))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(42.0)


def test_float_from_str_parses() -> None:
    result = _poop_float_from(Str("3.14"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.14)


def test_float_from_boolean() -> None:
    # float(True) -> 1.0, float(False) -> 0.0.
    assert _poop_float_from(true) == Float(1.0)
    assert _poop_float_from(false) == Float(0.0)


def test_float_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert complex to float"):
        _poop_float_from(Complex(complex(1, 2)))


def test_float_from_an_unparsable_string_names_the_value() -> None:
    # `could not convert string to float: 'abc'` names Python's type, not the
    # message the reader sent.
    with pytest.raises(ValueError, match=r"^'abc' is not a valid float$"):
        _poop_float_from(Str("abc"))


def test_float_refuses_a_keyword_argument() -> None:
    # Twin of the `bool(x=1)` guard: unconditionally rewritten, this answered
    # `0.0` off the helper's default instead of a TypeError. The converter
    # now calls `refuse_extra_arguments`, so the sentence is POOP's now
    # rather than CPython's `got an unexpected keyword argument`.
    with pytest.raises(ExecutionError, match="float takes no keyword arguments"):
        Interpreter().run_source("float(x=1).print()")
