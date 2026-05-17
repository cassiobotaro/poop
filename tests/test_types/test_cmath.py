import cmath as _cmath

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.cmath import CMath
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.tuple import Tuple

# --- Constants ---


def test_constant_pi_present() -> None:
    assert isinstance(CMath.pi, Float)
    assert CMath.pi._value == _cmath.pi


def test_constant_e_present() -> None:
    assert isinstance(CMath.e, Float)
    assert CMath.e._value == _cmath.e


def test_constant_tau_present() -> None:
    assert isinstance(CMath.tau, Float)
    assert CMath.tau._value == _cmath.tau


def test_constant_inf_present() -> None:
    assert isinstance(CMath.inf, Float)
    assert CMath.inf._value == _cmath.inf


def test_constant_nan_present() -> None:
    assert isinstance(CMath.nan, Float)
    assert _cmath.isnan(CMath.nan._value)


def test_constant_infj_present() -> None:
    assert isinstance(CMath.infj, Complex)
    assert CMath.infj._value == _cmath.infj


def test_constant_nanj_present() -> None:
    assert isinstance(CMath.nanj, Complex)
    assert _cmath.isnan(CMath.nanj._value.imag)


# --- Power & logarithmic ---


def test_sqrt_of_negative_one_is_imaginary_unit() -> None:
    result = CMath.sqrt(Complex(complex(-1, 0)))
    assert isinstance(result, Complex)
    assert result._value == pytest.approx(complex(0, 1))


def test_exp_of_zero_is_one() -> None:
    result = CMath.exp(Complex(complex(0, 0)))
    assert isinstance(result, Complex)
    assert result._value == pytest.approx(complex(1, 0))


def test_log_natural() -> None:
    result = CMath.log(Complex(complex(_cmath.e, 0)))
    assert isinstance(result, Complex)
    assert result._value.real == pytest.approx(1.0)


def test_log_with_base() -> None:
    result = CMath.log(Complex(complex(8, 0)), Complex(complex(2, 0)))
    assert isinstance(result, Complex)
    assert result._value.real == pytest.approx(3.0)


def test_log10() -> None:
    result = CMath.log10(Complex(complex(100, 0)))
    assert isinstance(result, Complex)
    assert result._value.real == pytest.approx(2.0)


# --- Trigonometric ---


@pytest.mark.parametrize(
    ("method", "x"),
    [
        ("sin", complex(0, 0)),
        ("cos", complex(0, 0)),
        ("tan", complex(0, 0)),
        ("asin", complex(0, 0)),
        ("acos", complex(1, 0)),
        ("atan", complex(0, 0)),
    ],
)
def test_trig_returns_complex(method: str, x: complex) -> None:
    result = getattr(CMath, method)(Complex(x))
    assert isinstance(result, Complex)
    assert result._value == pytest.approx(getattr(_cmath, method)(x))


# --- Hyperbolic ---


@pytest.mark.parametrize(
    ("method", "x"),
    [
        ("sinh", complex(0, 0)),
        ("cosh", complex(0, 0)),
        ("tanh", complex(0, 0)),
        ("asinh", complex(0, 0)),
        ("acosh", complex(1, 0)),
        ("atanh", complex(0, 0)),
    ],
)
def test_hyperbolic_returns_complex(method: str, x: complex) -> None:
    result = getattr(CMath, method)(Complex(x))
    assert isinstance(result, Complex)
    assert result._value == pytest.approx(getattr(_cmath, method)(x))


# --- Polar / rectangular ---


def test_phase_returns_float() -> None:
    result = CMath.phase(Complex(complex(0, 1)))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(_cmath.pi / 2)


def test_polar_returns_tuple_of_floats() -> None:
    result = CMath.polar(Complex(complex(1, 1)))
    assert isinstance(result, Tuple)
    r, phi = result._items
    assert isinstance(r, Float)
    assert isinstance(phi, Float)
    assert r._value == pytest.approx(_cmath.sqrt(2).real)
    assert phi._value == pytest.approx(_cmath.pi / 4)


def test_rect_returns_complex() -> None:
    result = CMath.rect(Float(1.0), Float(0.0))
    assert isinstance(result, Complex)
    assert result._value == pytest.approx(complex(1, 0))


def test_polar_rect_round_trip() -> None:
    original = Complex(complex(3, 4))
    polar = CMath.polar(original)
    r, phi = polar._items
    assert isinstance(r, Float)
    assert isinstance(phi, Float)
    restored = CMath.rect(r, phi)
    assert restored._value == pytest.approx(original._value)


# --- Predicates ---


def test_isfinite_true_for_finite() -> None:
    assert CMath.isfinite(Complex(complex(1, 2))) is true


def test_isfinite_false_if_any_part_nonfinite() -> None:
    assert CMath.isfinite(Complex(complex(_cmath.inf, 0))) is false
    assert CMath.isfinite(Complex(complex(0, _cmath.nan))) is false


def test_isinf_true_if_any_part_inf() -> None:
    assert CMath.isinf(Complex(complex(_cmath.inf, 0))) is true
    assert CMath.isinf(Complex(complex(0, _cmath.inf))) is true


def test_isinf_false_for_finite() -> None:
    assert CMath.isinf(Complex(complex(1, 2))) is false


def test_isnan_true_if_any_part_nan() -> None:
    assert CMath.isnan(Complex(complex(_cmath.nan, 0))) is true
    assert CMath.isnan(Complex(complex(0, _cmath.nan))) is true


def test_isnan_false_for_finite() -> None:
    assert CMath.isnan(Complex(complex(1, 2))) is false


def test_isclose_true_for_close_values() -> None:
    assert (
        CMath.isclose(Complex(complex(1.0, 0)), Complex(complex(1.0 + 1e-10, 0)))
        is true
    )


def test_isclose_false_for_distant_values() -> None:
    assert CMath.isclose(Complex(complex(1, 0)), Complex(complex(2, 0))) is false


def test_isclose_along_imaginary_axis() -> None:
    assert (
        CMath.isclose(Complex(complex(0, 1.0)), Complex(complex(0, 1.0 + 1e-10)))
        is true
    )


def test_isclose_with_abs_tol() -> None:
    assert (
        CMath.isclose(
            Complex(complex(1.0, 0)),
            Complex(complex(1.05, 0)),
            abs_tol=Float(0.1),
        )
        is true
    )


# --- Interpreter integration ---


def test_cmath_reachable_via_interpreter() -> None:
    Interpreter().run_source("cmath.sqrt(complex(-1, 0)).print()")


def test_cmath_constant_reachable_via_interpreter() -> None:
    Interpreter().run_source("cmath.pi.print()")
