import pytest

from poop.parser import parse
from poop.transformers.complex import (
    ComplexTransformer,
    _poop_complex_from,
    _poop_complex_literal,
)
from poop.transformers.int import IntTransformer
from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def test_real() -> None:
    assert Complex(1 + 2j).real._value == pytest.approx(1.0)


def test_imag() -> None:
    assert Complex(1 + 2j).imag._value == pytest.approx(2.0)


def test_real_zero_imag() -> None:
    assert Complex(3j).real._value == pytest.approx(0.0)
    assert Complex(3j).imag._value == pytest.approx(3.0)


def test_conjugate() -> None:
    assert Complex(1 + 2j).conjugate() == Complex(1 - 2j)


def test_abs() -> None:
    result = Complex(3 + 4j).abs()
    assert isinstance(result, Float)
    assert result._value == pytest.approx(5.0)


def test_dunder_abs() -> None:
    assert abs(Complex(3 + 4j))._value == pytest.approx(5.0)


def test_negated() -> None:
    assert Complex(1 + 2j).negated() == Complex(-1 - 2j)


def test_dunder_neg() -> None:
    assert -Complex(2j) == Complex(-2j)


def test_add_complex() -> None:
    assert Complex(1 + 2j) + Complex(3 + 4j) == Complex(4 + 6j)


def test_add_int() -> None:
    assert Complex(1 + 2j) + Int(3) == Complex(4 + 2j)


def test_add_float() -> None:
    assert Complex(1 + 2j) + Float(0.5) == Complex(1.5 + 2j)


def test_radd_int() -> None:
    # Complex.__radd__ handles Int + Complex at runtime via Python's operator protocol
    assert Complex(1 + 2j).__radd__(Int(3)) == Complex(4 + 2j)


# Regression: Int/Float arithmetic with a Complex right operand must yield a
# real Complex (Int/Float.__op__ return NotImplemented so Complex.__r__ fires),
# not a corrupted Int/Float wrapper holding a Python complex. These exercise the
# actual operator path, unlike the direct __radd__ call above.
def test_int_plus_complex_yields_complex() -> None:
    result = Int(3) + Complex(1 + 2j)
    assert isinstance(result, Complex)
    assert result == Complex(4 + 2j)


def test_int_minus_complex_yields_complex() -> None:
    result = Int(3) - Complex(1 + 2j)
    assert isinstance(result, Complex)
    assert result == Complex(2 - 2j)


def test_int_times_complex_yields_complex() -> None:
    result = Int(3) * Complex(1 + 2j)
    assert isinstance(result, Complex)
    assert result == Complex(3 + 6j)


def test_int_div_complex_yields_complex() -> None:
    result = Int(4) / Complex(2 + 0j)
    assert isinstance(result, Complex)
    assert result == Complex(2 + 0j)


def test_int_pow_complex_yields_complex() -> None:
    result = Int(2) ** Complex(1 + 0j)
    assert isinstance(result, Complex)
    assert result == Complex(2 + 0j)


def test_float_plus_complex_yields_complex() -> None:
    result = Float(0.5) + Complex(1 + 2j)
    assert isinstance(result, Complex)
    assert result == Complex(1.5 + 2j)


def test_float_times_complex_yields_complex() -> None:
    result = Float(2.0) * Complex(1 + 2j)
    assert isinstance(result, Complex)
    assert result == Complex(2 + 4j)


def test_float_pow_complex_yields_complex() -> None:
    result = Float(2.0) ** Complex(1 + 0j)
    assert isinstance(result, Complex)
    assert result == Complex(2 + 0j)


def test_sub_complex() -> None:
    assert Complex(5 + 6j) - Complex(1 + 2j) == Complex(4 + 4j)


def test_mul_complex() -> None:
    assert Complex(1 + 1j) * Complex(1 - 1j) == Complex(2 + 0j)


def test_mul_int() -> None:
    assert Complex(1 + 2j) * Int(3) == Complex(3 + 6j)


def test_truediv_complex() -> None:
    result = Complex(4 + 0j) / Complex(2 + 0j)
    assert result == Complex(2 + 0j)


def test_pow_complex() -> None:
    assert Complex(1j) ** Int(2) == Complex(-1 + 0j)


def test_eq_equal() -> None:
    assert Complex(1 + 2j) == Complex(1 + 2j)


def test_eq_different() -> None:
    assert (Complex(1 + 2j) == Complex(3 + 4j)) is false


def test_ne_different() -> None:
    assert (Complex(1 + 2j) != Complex(3 + 4j)) is true


def test_eq_with_int_equal() -> None:
    # CPython: complex(1, 0) == 1 is True.
    assert Complex(1 + 0j) == Int(1)
    assert (Complex(1 + 0j) != Int(1)) is false


def test_eq_with_int_unequal_when_imaginary() -> None:
    assert (Complex(1 + 2j) == Int(1)) is false
    assert (Complex(1 + 2j) != Int(1)) is true


def test_eq_with_float() -> None:
    assert Complex(1 + 0j) == Float(1.0)
    assert (Complex(1 + 0j) == Float(2.0)) is false


def test_eq_with_boolean() -> None:
    assert Complex(1 + 0j) == true
    assert Complex(0 + 0j) == false
    assert (Complex(1 + 0j) == false) is false


def test_eq_with_foreign_type_returns_false() -> None:
    assert (Complex(1 + 0j) == Str("x")) is false
    assert (Complex(1 + 0j) != Str("x")) is true


def test_hashable() -> None:
    assert isinstance(hash(Complex(1 + 2j)), int)


def test_equal_complex_same_hash() -> None:
    assert hash(Complex(1 + 2j)) == hash(Complex(1 + 2j))


def test_complex_can_be_dict_key() -> None:
    d = Dict()
    d.at_put(Complex(1 + 2j), Int(42))
    assert d.at(Complex(1 + 2j)) == Int(42)


def test_str_representation() -> None:
    assert str(Complex(1 + 2j)) == "(1+2j)"


def test_str_pure_imaginary() -> None:
    assert str(Complex(2j)) == "2j"


def test_repr_equals_str() -> None:
    c = Complex(1 + 2j)
    assert repr(c) == str(c)


def test_bool_zero_is_falsy() -> None:
    # `bool(0j)` is False in CPython — Complex must not inherit Object's
    # always-truthy default.
    assert bool(Complex(0j)) is False
    assert bool(Complex(complex(0, 0))) is False


def test_bool_nonzero_is_truthy() -> None:
    assert bool(Complex(1j)) is True
    assert bool(Complex(3 + 0j)) is True
    assert bool(Complex(0 + 4j)) is True


def test_not_on_zero_complex_is_true() -> None:
    assert Complex(0j).not_() is true
    assert Complex(1j).not_() is false


def test_assert_on_zero_complex_raises() -> None:
    with pytest.raises(AssertionError):
        Complex(0j).assert_()


def test_transformer_j_literal() -> None:
    tree = parse("c = 2j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(2j)


def test_transformer_negative_j_literal() -> None:
    tree = parse("c = -2j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(-2j)


def test_transformer_binop_literal() -> None:
    tree = parse("c = 1+2j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_transformer_binop_sub_literal() -> None:
    tree = parse("c = 3-1j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(3 - 1j)


def test_transformer_complex_call_no_args() -> None:
    tree = parse("c = complex()")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_from": _poop_complex_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["c"], Complex)
    assert ns["c"] == Complex(0j)  # type: ignore[union-attr]


def test_transformer_complex_call_two_args() -> None:
    tree = parse("c = complex(1, 2)")
    tree = IntTransformer().transform(tree)
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_int": Int, "_poop_complex_from": _poop_complex_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_transformer_does_not_affect_int_literals() -> None:
    tree = ComplexTransformer().transform(parse("x = 42"))
    ns: dict[str, object] = {}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert ns["x"] == 42  # noqa: PLR2004


def test_complex_from_str() -> None:
    result = _poop_complex_from(Str("1+2j"))
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_complex_from_int() -> None:
    result = _poop_complex_from(Int(5))
    assert result == Complex(5 + 0j)


def test_complex_from_float() -> None:
    result = _poop_complex_from(Float(2.5))
    assert result == Complex(2.5 + 0j)


def test_complex_from_existing_complex() -> None:
    c = Complex(1 + 2j)
    assert _poop_complex_from(c) is c


def test_not_equal_to_non_complex() -> None:
    assert (Complex(1 + 2j) == Int(1)) is false


def test_ne_non_complex() -> None:
    assert (Complex(1 + 2j) != Int(1)) is true


# Reverse operators


def test_rsub_int() -> None:
    assert Complex(5 + 0j).__rsub__(Int(10)) == Complex(5 + 0j)


def test_rmul_int() -> None:
    assert Complex(1 + 2j).__rmul__(Int(3)) == Complex(3 + 6j)


def test_rtruediv_int() -> None:
    assert Complex(2 + 0j).__rtruediv__(Int(4)) == Complex(2 + 0j)


def test_rpow_int() -> None:
    assert Complex(1 + 0j).__rpow__(Int(2)) == Complex(2 + 0j)


# NotImplemented paths — unsupported operand type


def test_add_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__add__(Str("x")) is NotImplemented


def test_radd_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__radd__(Str("x")) is NotImplemented


def test_sub_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__sub__(Str("x")) is NotImplemented


def test_rsub_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__rsub__(Str("x")) is NotImplemented


def test_mul_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__mul__(Str("x")) is NotImplemented


def test_rmul_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__rmul__(Str("x")) is NotImplemented


def test_truediv_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__truediv__(Str("x")) is NotImplemented


def test_rtruediv_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__rtruediv__(Str("x")) is NotImplemented


def test_pow_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__pow__(Str("x")) is NotImplemented


def test_rpow_unsupported_returns_not_implemented() -> None:
    assert Complex(1 + 2j).__rpow__(Str("x")) is NotImplemented


@pytest.mark.parametrize(
    ("c", "expected"),
    [
        (Complex(0j), "0j"),
        (Complex(1 + 0j), "(1+0j)"),
        (Complex(-1 - 1j), "(-1-1j)"),
    ],
)
def test_str_various(c: Complex, expected: str) -> None:
    assert str(c) == expected


def test_complex_from_unsupported_real_type_raises() -> None:
    with pytest.raises(TypeError, match="Dict"):
        _poop_complex_from(Dict())


def test_complex_from_unsupported_first_of_two_args_raises() -> None:
    with pytest.raises(TypeError, match="Dict"):
        _poop_complex_from(Dict(), Int(1))


def test_complex_from_unsupported_second_of_two_args_raises() -> None:
    with pytest.raises(TypeError, match="Dict"):
        _poop_complex_from(Int(1), Dict())
