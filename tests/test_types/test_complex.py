import pytest

from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def test_real() -> None:
    assert Complex(1 + 2j).real() == Float(1.0)


def test_imag() -> None:
    assert Complex(1 + 2j).imag() == Float(2.0)


def test_real_zero_imag() -> None:
    assert Complex(3j).real() == Float(0.0)
    assert Complex(3j).imag() == Float(3.0)


def test_conjugate() -> None:
    assert Complex(1 + 2j).conjugate() == Complex(1 - 2j)


def test_abs() -> None:
    result = Complex(3 + 4j).abs()
    assert isinstance(result, Float)
    assert result == Float(5.0)


def test_dunder_abs() -> None:
    assert abs(Complex(3 + 4j)) == Float(5.0)


def test_negated() -> None:
    assert Complex(1 + 2j).negated() == Complex(-1 - 2j)


def test_add_complex() -> None:
    assert Complex(1 + 2j) + Complex(3 + 4j) == Complex(4 + 6j)


def test_add_int() -> None:
    assert Complex(1 + 2j) + Int(3) == Complex(4 + 2j)


def test_add_float() -> None:
    assert Complex(1 + 2j) + Float(0.5) == Complex(1.5 + 2j)


def test_radd_int() -> None:
    # Complex.__radd__ handles Int + Complex at runtime via Python's operator protocol
    assert Complex(1 + 2j).__radd__(Int(3)) == Complex(4 + 2j)


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


def test_hashable() -> None:
    assert isinstance(hash(Complex(1 + 2j)), int)


def test_equal_complex_same_hash() -> None:
    assert hash(Complex(1 + 2j)) == hash(Complex(1 + 2j))


def test_complex_can_be_dict_key() -> None:
    from poop.types.dict import Dict

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


def test_transformer_j_literal() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer, _poop_complex_literal

    tree = parse("c = 2j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(2j)


def test_transformer_binop_literal() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer, _poop_complex_literal

    tree = parse("c = 1+2j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_transformer_binop_sub_literal() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer, _poop_complex_literal

    tree = parse("c = 3-1j")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_literal": _poop_complex_literal}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(3 - 1j)


def test_transformer_complex_call_no_args() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer, _poop_complex_from

    tree = parse("c = complex()")
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_complex_from": _poop_complex_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["c"], Complex)
    assert ns["c"] == Complex(0j)  # type: ignore[union-attr]


def test_transformer_complex_call_two_args() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer, _poop_complex_from
    from poop.transformers.int import IntTransformer

    tree = parse("c = complex(1, 2)")
    tree = IntTransformer().transform(tree)
    tree = ComplexTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_int": Int, "_poop_complex_from": _poop_complex_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["c"]
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_transformer_does_not_affect_int_literals() -> None:
    from poop.parser import parse
    from poop.transformers.complex import ComplexTransformer

    tree = ComplexTransformer().transform(parse("x = 42"))
    ns: dict[str, object] = {}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert ns["x"] == 42  # noqa: PLR2004


def test_complex_from_str() -> None:
    from poop.transformers.complex import _poop_complex_from

    result = _poop_complex_from(Str("1+2j"))
    assert isinstance(result, Complex)
    assert result == Complex(1 + 2j)


def test_complex_from_int() -> None:
    from poop.transformers.complex import _poop_complex_from

    result = _poop_complex_from(Int(5))
    assert result == Complex(5 + 0j)


def test_complex_from_float() -> None:
    from poop.transformers.complex import _poop_complex_from

    result = _poop_complex_from(Float(2.5))
    assert result == Complex(2.5 + 0j)


def test_complex_from_existing_complex() -> None:
    from poop.transformers.complex import _poop_complex_from

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
