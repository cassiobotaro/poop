from typing import Any

import pytest

from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


class _ForeignNumber:
    """A type Float knows nothing about.

    Stands in for any third-party number: Float must answer
    NotImplemented rather than reach into a `_value` this type lacks.
    """


def test_str() -> None:
    assert str(Float(3.14)) == "3.14"


def test_repr_delegates_to_str() -> None:
    assert repr(Float(3.14)) == "3.14"


def test_float_conversion() -> None:
    assert float(Float(2.5)) == pytest.approx(2.5)


def test_bool_nonzero_is_true() -> None:
    assert bool(Float(1.0)) is True


def test_bool_zero_is_false() -> None:
    assert bool(Float(0.0)) is False


def test_negated() -> None:
    assert Float(3.0).negated()._value == pytest.approx(-3.0)


def test_negated_negative() -> None:
    assert Float(-2.5).negated()._value == pytest.approx(2.5)


def test_max_returns_larger() -> None:
    assert Float(1.5).max(Float(2.5))._value == pytest.approx(2.5)
    assert Float(2.5).max(Float(1.5))._value == pytest.approx(2.5)


def test_min_returns_smaller() -> None:
    assert Float(1.5).min(Float(2.5))._value == pytest.approx(1.5)
    assert Float(2.5).min(Float(1.5))._value == pytest.approx(1.5)


def test_max_is_variadic() -> None:
    assert Float(1.5).max(Float(2.5), Float(0.5))._value == pytest.approx(2.5)
    assert Float(3.5).max()._value == pytest.approx(3.5)


def test_min_is_variadic() -> None:
    assert Float(1.5).min(Float(2.5), Float(0.5))._value == pytest.approx(0.5)
    assert Float(3.5).min()._value == pytest.approx(3.5)


def test_min_max_accept_the_rest_of_the_numeric_tower() -> None:
    # An Int or a Boolean orders against a Float in CPython; reading
    # `other._value` was fine for Int and leaked for a foreign operand.
    assert Float(1.5).max(Int(2)) == Int(2)
    assert Float(0.5).min(true) == Float(0.5)


@pytest.mark.parametrize("message", ["max", "min"])
def test_min_max_foreign_operand_is_faithful_not_a_value_leak(message: str) -> None:
    with pytest.raises(TypeError) as info:
        getattr(Float(1.0), message)(List(Int(2)))
    assert "_value" not in str(info.value)


def test_add() -> None:
    assert (Float(1.5) + Float(2.5))._value == pytest.approx(4.0)


def test_sub() -> None:
    assert (Float(5.0) - Float(2.0))._value == pytest.approx(3.0)


def test_mul() -> None:
    assert (Float(2.0) * Float(3.0))._value == pytest.approx(6.0)


def test_truediv() -> None:
    assert (Float(7.0) / Float(2.0))._value == pytest.approx(3.5)


def test_mod() -> None:
    assert (Float(7.0) % Float(3.0))._value == pytest.approx(1.0)


def test_arithmetic_returns_notimplemented_for_foreign_operand() -> None:
    # A non-Int/Float operand must yield NotImplemented so Python can try the
    # right operand's reflected dunder (proposal 115).
    f = _ForeignNumber()
    assert Float(2.5).__add__(f) is NotImplemented
    assert Float(2.5).__sub__(f) is NotImplemented
    assert Float(2.5).__mul__(f) is NotImplemented
    assert Float(2.5).__truediv__(f) is NotImplemented
    assert Float(2.5).__floordiv__(f) is NotImplemented
    assert Float(2.5).__mod__(f) is NotImplemented


def test_arithmetic_with_int_operand_still_works() -> None:
    assert (Float(2.5) + Int(2))._value == pytest.approx(4.5)
    assert (Float(2.5) * Int(2))._value == pytest.approx(5.0)


def test_pow() -> None:
    assert (Float(2.0) ** Float(3.0))._value == pytest.approx(8.0)


def test_pow_negative_base_fractional_exponent_returns_complex() -> None:
    result = Float(-1.0) ** Float(0.5)
    assert isinstance(result, Complex)
    assert result == Complex((-1.0) ** 0.5)


def test_eq_returns_boolean() -> None:
    assert Float(1.5).__eq__(Float(1.5)) is true
    assert Float(1.5).__eq__(Float(2.5)) is false


def test_eq_with_non_float_returns_false() -> None:
    assert Float(1.5).__eq__(1.5) is false


def test_eq_with_complex_real_match() -> None:
    # CPython: `2.0 == (2+0j)` is True — Float joins the numeric tower.
    assert Float(2.0) == Complex(2 + 0j)


def test_eq_with_complex_imaginary_part_differs() -> None:
    assert (Float(2.0) == Complex(2 + 1j)) is false
    assert (Float(2.0) != Complex(2 + 1j)) is true


def test_ne_with_complex_real_match() -> None:
    assert (Float(2.0) != Complex(2 + 0j)) is false


def test_ne_returns_boolean() -> None:
    assert Float(1.5).__ne__(Float(2.5)) is true
    assert Float(1.5).__ne__(Float(1.5)) is false


def test_ne_with_non_float_returns_true() -> None:
    assert Float(1.5).__ne__(1.5) is true


def test_lt_returns_boolean() -> None:
    assert Float(1.0).__lt__(Float(2.0)) is true
    assert Float(2.0).__lt__(Float(1.0)) is false


def test_le_returns_boolean() -> None:
    assert Float(1.0).__le__(Float(1.0)) is true
    assert Float(2.0).__le__(Float(1.0)) is false


def test_gt_returns_boolean() -> None:
    assert Float(2.0).__gt__(Float(1.0)) is true
    assert Float(1.0).__gt__(Float(2.0)) is false


def test_ge_returns_boolean() -> None:
    assert Float(2.0).__ge__(Float(2.0)) is true
    assert Float(1.0).__ge__(Float(2.0)) is false


def test_hashable() -> None:
    assert hash(Float(1.5)) == hash(1.5)


def test_is_none_inherited() -> None:
    assert Float(1.0).is_none() is false


def test_class_name() -> None:
    assert Float(1.0).class_name() == Str("float")


def test_abs_positive() -> None:
    assert Float(3.5).abs()._value == pytest.approx(3.5)


def test_abs_negative() -> None:
    assert Float(-3.5).abs()._value == pytest.approx(3.5)


def test_dunder_abs() -> None:
    assert abs(Float(-2.0))._value == pytest.approx(2.0)


def test_ceil_returns_int() -> None:
    assert Float(2.3).ceil() == Int(3)


def test_floor_returns_int() -> None:
    assert Float(2.7).floor() == Int(2)


def test_trunc_returns_int() -> None:
    assert Float(2.9).trunc() == Int(2)
    assert Float(-2.9).trunc() == Int(-2)


def test_round_no_digits_returns_int() -> None:
    assert Float(2.5).round() == Int(2)
    assert Float(3.5).round() == Int(4)


def test_round_with_digits_returns_float() -> None:
    assert Float(3.14159).round(Int(2))._value == pytest.approx(3.14)
    assert Float(3.456).round(Int(1))._value == pytest.approx(3.5)


def test_round_accepts_poop_none() -> None:
    from poop.types.none import none

    assert Float(2.5).round(none) == Int(2)


def test_int_conversion() -> None:
    assert int(Float(3.9)) == 3


def test_complex_constructor() -> None:
    from poop.transformers.complex import _poop_complex_from

    assert _poop_complex_from(Float(2.5)) == Complex(2.5 + 0j)


def test_is_integer_true() -> None:
    assert Float(3.0).is_integer() is true


def test_is_integer_false() -> None:
    assert Float(3.5).is_integer() is false


def test_floordiv() -> None:
    assert (Float(7.0) // Float(2.0))._value == pytest.approx(3.0)


def test_int_truncates() -> None:
    from poop.transformers.int import _poop_int_from

    assert _poop_int_from(Float(3.7)) == Int(3)
    assert _poop_int_from(Float(-2.9)) == Int(-2)


def test_float_constructor_identity() -> None:
    from poop.transformers.float import _poop_float_from

    f = Float(1.5)
    assert _poop_float_from(f) is f


def test_conjugate_returns_self() -> None:
    f = Float(3.5)
    assert f.conjugate() is f


def test_hex_returns_str() -> None:
    assert Float(1.0).hex() == Str("0x1.0000000000000p+0")


def test_real_returns_self() -> None:
    f = Float(2.5)
    assert f.real() is f


def test_imag_returns_zero() -> None:
    assert Float(2.5).imag()._value == pytest.approx(0.0)


def test_as_integer_ratio() -> None:
    n, d = Float(0.5).as_integer_ratio()._items
    assert n == Int(1)
    assert d == Int(2)


def test_pow_method() -> None:
    assert Float(2.0).pow(Float(3.0))._value == pytest.approx(8.0)


def test_fromhex_parses_hex_string() -> None:
    result = Float.fromhex(Str("0x1.8p+0"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(1.5)


def test_fromhex_roundtrips_with_hex() -> None:
    f = Float(3.14)
    assert Float.fromhex(f.hex()) == f


# --- Cross-POOP-type numeric equality (proposal 86) ---


def test_eq_with_int_same_value() -> None:
    from poop.types.int import Int

    assert Float(1.0) == Int(1)
    assert Float(2.5) != Int(2)


def test_ne_with_int_same_value() -> None:
    from poop.types.int import Int

    assert (Float(1.0) != Int(1)) is false
    assert (Float(2.5) != Int(2)) is true


def test_ne_with_non_numeric_returns_true() -> None:
    assert (Float(1.5) != "1.5") is true


def test_ceil_floor_trunc_protocol() -> None:
    # __ceil__/__floor__/__trunc__ used by math.ceil/floor/trunc
    import math

    assert math.ceil(Float(3.2)) == Int(4)
    assert math.floor(Float(3.7)) == Int(3)
    assert math.trunc(Float(3.7)) == Int(3)


def test_divmod_with_int() -> None:
    assert Float(7.5).divmod(Int(2)) == Tuple(Float(3.0), Float(1.5))


def test_divmod_folds_boolean() -> None:
    # bool is an int subclass: divmod(7.0, True) == (7.0, 0.0)
    assert Float(7.0).divmod(true) == Tuple(Float(7.0), Float(0.0))


def test_divmod_dunder_returns_notimplemented_for_foreign_operand() -> None:
    assert Float(7.0).__divmod__("x") is NotImplemented


def test_divmod_method_raises_typeerror_for_foreign_operand() -> None:
    with pytest.raises(TypeError):
        Float(7.0).divmod("x")


def test_pow_method_raises_typeerror_for_foreign_operand() -> None:
    # pow() must not leak the raw NotImplemented singleton to user code.
    with pytest.raises(TypeError):
        Float(2.0).pow("x")


_BAD: Any = List(Int(1), Int(2))


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(lambda: Float.fromhex(_BAD), TypeError, id="fromhex"),
        pytest.param(lambda: Float(5.0).round(_BAD), TypeError, id="round"),
    ],
)
def test_float_wrong_type_arg_is_faithful_not_value_leak(call, exc) -> None:
    # proposals.md item 9: a mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_min_max_take_a_key_like_the_builtin() -> None:
    # Same gap the Int rung had: without `key` the block was compared as a
    # value rather than applied to the operands.
    assert Float(5.5).max(Float(3.0), key=lambda n: n.negated()) == Float(3.0)
    assert Float(5.5).min(Float(3.0), key=lambda n: n.negated()) == Float(5.5)


def test_pow_completes_the_reflected_protocol_for_a_complex() -> None:
    from poop.types.complex import Complex

    assert Float(2.0).pow(Complex(complex(1, 1))) == Float(2.0) ** Complex(
        complex(1, 1)
    )


def test_pow_refusal_names_the_message_not_the_operator() -> None:
    with pytest.raises(TypeError, match=r"float does not understand #pow with a str"):
        Float(2.0).pow("x")


def test_pow_takes_a_modulus_slot_and_refuses_it_as_an_operation() -> None:
    # Without the third slot, `(2.0).pow(3, 5)` answered CPython's signature
    # error — `float.pow() takes 2 positional arguments but 3 were given` —
    # while `(2).pow(3.0, 5)` answered the operation. Same message, same
    # mistake, two vocabularies.
    with pytest.raises(TypeError, match="modulus is only defined when both operands"):
        Float(2.0).pow(Int(3), Int(5))


def test_an_absent_modulus_still_computes() -> None:
    assert Float(2.0).pow(Int(3)) == Float(8.0)
    assert Float(2.0).pow(Int(3), none) == Float(8.0)


def test_fromhex_under_the_bare_builtin_name() -> None:
    # The third of the three: `cannot convert float to float`.
    from poop.transformers.float import FloatTransformer

    alias = FloatTransformer.BINDINGS["_poop_float_cls"]
    assert alias.fromhex(Str("0x1.8p+1")) == Float(3.0)  # ty: ignore[unresolved-attribute]
    assert Float(1.0).fromhex(Str("0x1.8p+1")) == Float(3.0)


def test_fromhex_names_the_message_like_its_byte_twins() -> None:
    # Proposal 52: `bad argument type for built-in operation` names neither the
    # receiver, the message nor the argument, while `Bytes.fromhex` and
    # `ByteArray.fromhex` already answered `#fromhex expects a str, got an int`.
    with pytest.raises(TypeError, match="#fromhex expects a str"):
        Float.fromhex(Int(5))  # ty: ignore[invalid-argument-type]
