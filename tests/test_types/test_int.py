from typing import Any

import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


class _ForeignNumber:
    """A type Int knows nothing about, with a reflected dunder to reach.

    Stands in for any third-party number: Int must answer NotImplemented
    rather than reach into a `_value` this type does not have.
    """

    def __radd__(self, other: object) -> tuple[str, object]:
        return ("radd", other)


def test_str() -> None:
    assert str(Int(42)) == "42"


def test_repr_delegates_to_str() -> None:
    assert repr(Int(42)) == "42"


def test_int_conversion() -> None:
    assert int(Int(7)) == 7


def test_bool_nonzero_is_true() -> None:
    assert bool(Int(1)) is True


def test_bool_zero_is_false() -> None:
    assert bool(Int(0)) is False


def test_negated() -> None:
    assert Int(3).negated() == Int(-3)


def test_negated_negative() -> None:
    assert Int(-5).negated() == Int(5)


def test_bit_invert() -> None:
    assert Int(0).bit_invert() == Int(-1)
    assert Int(1).bit_invert() == Int(-2)


def test_max_returns_larger() -> None:
    assert Int(3).max(Int(7)) == Int(7)
    assert Int(7).max(Int(3)) == Int(7)


def test_min_returns_smaller() -> None:
    assert Int(3).min(Int(7)) == Int(3)
    assert Int(7).min(Int(3)) == Int(3)


def test_max_is_variadic() -> None:
    assert Int(3).max(Int(7), Int(5)) == Int(7)
    assert Int(9).max(Int(1), Int(4)) == Int(9)
    assert Int(5).max() == Int(5)


def test_min_is_variadic() -> None:
    assert Int(3).min(Int(7), Int(1)) == Int(1)
    assert Int(2).min(Int(8), Int(6)) == Int(2)
    assert Int(5).min() == Int(5)


def test_max_returns_first_on_tie() -> None:
    first = Int(5)
    assert first.max(Int(5)) is first


def test_min_returns_first_on_tie() -> None:
    first = Int(5)
    assert first.min(Int(5)) is first


def test_min_max_accept_a_boolean() -> None:
    # bool is an int subclass in CPython: min(1, True) == 1, max(0, True) is
    # True. Reading `other._value` used to answer "bool does not understand
    # #_value" instead.
    assert Int(1).min(true) == Int(1)
    assert Int(0).max(true) is true
    assert Int(1).min(false) is false


def test_min_max_take_a_key_like_the_builtin() -> None:
    # `max(5, 3, key=lambda x: -x)` is 3 in CPython. Without `key` the block
    # was swallowed as one more operand, so a *comparable* extra argument
    # would have answered a plausible wrong number in silence.
    assert Int(5).max(Int(3), key=lambda n: n.negated()) == Int(3)
    assert Int(5).min(Int(3), key=lambda n: n.negated()) == Int(5)


def test_min_max_key_is_keyword_only() -> None:
    # Positionally it is indistinguishable from a third operand, and reading it
    # as one is the bug: a block compared as a value answers nonsense.
    with pytest.raises(TypeError):
        Int(5).max(Int(3), lambda n: n.negated())  # ty: ignore[invalid-argument-type]


def test_min_max_refuse_a_default_as_cpython_does() -> None:
    # "Cannot specify a default for max() with multiple positional arguments" —
    # the scalar form has operands, so there is nothing to default to.
    with pytest.raises(TypeError):
        Int(5).max(Int(3), default=Int(0))  # ty: ignore[unknown-argument]


@pytest.mark.parametrize("message", ["max", "min"])
def test_min_max_foreign_operand_is_faithful_not_a_value_leak(message: str) -> None:
    with pytest.raises(TypeError) as info:
        getattr(Int(1), message)(List(Int(2)))
    assert "_value" not in str(info.value)


def test_add() -> None:
    assert Int(2) + Int(3) == Int(5)


def test_sub() -> None:
    assert Int(5) - Int(2) == Int(3)


def test_mul() -> None:
    assert Int(3) * Int(4) == Int(12)


def test_floordiv() -> None:
    assert Int(7) // Int(2) == Int(3)


def test_mod() -> None:
    assert Int(7) % Int(3) == Int(1)


def test_arithmetic_returns_notimplemented_for_foreign_operand() -> None:
    # A non-Int/Float operand must yield NotImplemented so Python can try the
    # right operand's reflected dunder (proposal 115).
    f = _ForeignNumber()
    assert Int(2).__add__(f) is NotImplemented
    assert Int(2).__sub__(f) is NotImplemented
    assert Int(2).__mul__(f) is NotImplemented
    assert Int(2).__truediv__(f) is NotImplemented
    assert Int(2).__floordiv__(f) is NotImplemented
    assert Int(2).__mod__(f) is NotImplemented


def test_reflected_add_reaches_foreign_radd() -> None:
    # NotImplemented is only half the contract: CPython must then reach the
    # foreign operand's __radd__, handing it the Int untouched.
    assert Int(2) + _ForeignNumber() == ("radd", Int(2))


def test_mul_by_str_repeats_via_str_rmul() -> None:
    # proposal 152: 3 * "ab" must answer Str("ababab"), not a corrupted Int.
    assert Int(3) * Str("ab") == Str("ababab")


def test_mul_by_str_is_notimplemented() -> None:
    assert Int(3).__mul__(Str("ab")) is NotImplemented


def test_pow() -> None:
    assert Int(2) ** Int(10) == Int(1024)


def test_pow_negative_base_fractional_exponent_returns_complex() -> None:
    result = Int(-8) ** Float(0.5)
    assert isinstance(result, Complex)
    assert result == Complex((-8) ** 0.5)


def test_pow_with_modulus_rejects_float_exponent() -> None:
    with pytest.raises(TypeError, match="modulus is only defined when both operands"):
        Int(2).__pow__(Float(0.5), Int(3))


def test_eq_returns_boolean() -> None:
    assert Int(5).__eq__(Int(5)) is true
    assert Int(5).__eq__(Int(6)) is false


def test_eq_with_non_int_returns_false() -> None:
    assert Int(5).__eq__(42) is false


def test_eq_with_complex_real_match() -> None:
    # CPython: `1 == (1+0j)` is True — Int joins the numeric tower.
    assert Int(1) == Complex(1 + 0j)
    assert Int(0) == Complex(0j)


def test_eq_with_complex_imaginary_part_differs() -> None:
    assert (Int(1) == Complex(1 + 1j)) is false
    assert (Int(1) != Complex(1 + 1j)) is true


def test_ne_with_complex_real_match() -> None:
    assert (Int(1) != Complex(1 + 0j)) is false


def test_ne_returns_boolean() -> None:
    assert Int(5).__ne__(Int(6)) is true
    assert Int(5).__ne__(Int(5)) is false


def test_ne_with_non_int_returns_true() -> None:
    assert Int(5).__ne__(42) is true


def test_lt_returns_boolean() -> None:
    assert Int(3).__lt__(Int(5)) is true
    assert Int(5).__lt__(Int(3)) is false


def test_le_returns_boolean() -> None:
    assert Int(3).__le__(Int(3)) is true
    assert Int(5).__le__(Int(3)) is false


def test_gt_returns_boolean() -> None:
    assert Int(5).__gt__(Int(3)) is true
    assert Int(3).__gt__(Int(5)) is false


def test_ge_returns_boolean() -> None:
    assert Int(5).__ge__(Int(5)) is true
    assert Int(3).__ge__(Int(5)) is false


def test_hashable() -> None:
    assert hash(Int(42)) == hash(42)


def test_is_none_inherited() -> None:
    assert Int(1).is_none() is false


def test_class_name() -> None:
    assert Int(1).class_name() == Str("int")


@pytest.mark.parametrize("value", [0, 1, -1, 100])
def test_roundtrip_str(value: int) -> None:
    assert str(Int(value)) == str(value)


def test_abs_positive() -> None:
    assert Int(5).abs() == Int(5)


def test_abs_negative() -> None:
    assert Int(-5).abs() == Int(5)


def test_dunder_abs() -> None:
    assert abs(Int(-3)) == Int(3)


def test_truediv_returns_float() -> None:
    result = Int(7) / Int(2)
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.5)


def test_lshift() -> None:
    assert Int(1) << Int(3) == Int(8)


def test_rshift() -> None:
    assert Int(8) >> Int(2) == Int(2)


def test_bitwise_and() -> None:
    assert Int(0b1100) & Int(0b1010) == Int(0b1000)


def test_bitwise_or() -> None:
    assert Int(0b1100) | Int(0b1010) == Int(0b1110)


def test_bitwise_xor() -> None:
    assert Int(0b1100) ^ Int(0b1010) == Int(0b0110)


def test_bitwise_and_folds_boolean_as_one() -> None:
    # bool is an int subclass: 5 & True == 1
    assert Int(5) & true == Int(1)
    assert Int(5) & false == Int(0)


def test_bitwise_or_xor_fold_boolean() -> None:
    assert Int(6) | true == Int(7)
    assert Int(5) ^ true == Int(4)


def test_shift_folds_boolean() -> None:
    assert Int(1) << true == Int(2)
    assert Int(5) >> true == Int(2)


def test_bitwise_returns_notimplemented_for_foreign_operand() -> None:
    # Foreign / float operands must yield NotImplemented so CPython raises a
    # faithful TypeError instead of leaking an AttributeError on other._value.
    assert Int(5).__and__("x") is NotImplemented
    assert Int(5).__or__(Float(2.0)) is NotImplemented
    assert Int(5).__xor__("x") is NotImplemented
    assert Int(1).__lshift__(Float(2.0)) is NotImplemented
    assert Int(8).__rshift__("x") is NotImplemented


def test_divmod_with_int() -> None:
    assert Int(7).divmod(Int(2)) == Tuple(Int(3), Int(1))


def test_divmod_folds_boolean() -> None:
    assert Int(7).divmod(true) == Tuple(Int(7), Int(0))


def test_divmod_with_float_returns_floats() -> None:
    assert Int(7).divmod(Float(2.0)) == Tuple(Float(3.0), Float(1.0))


def test_divmod_dunder_returns_notimplemented_for_foreign_operand() -> None:
    assert Int(7).__divmod__("x") is NotImplemented


def test_divmod_method_raises_typeerror_for_foreign_operand() -> None:
    with pytest.raises(TypeError):
        Int(7).divmod("x")


def test_pow_method_raises_typeerror_for_foreign_operand() -> None:
    # pow() must not leak the raw NotImplemented singleton to user code.
    with pytest.raises(TypeError):
        Int(2).pow("x")


def test_ceil_returns_self() -> None:
    assert Int(5).ceil() == Int(5)


def test_floor_returns_self() -> None:
    assert Int(5).floor() == Int(5)


def test_trunc_returns_self() -> None:
    assert Int(5).trunc() == Int(5)


def test_round_returns_self() -> None:
    assert Int(5).round() == Int(5)


def test_round_with_poop_int_ndigits() -> None:
    assert Int(123).round(Int(-1)) == Int(120)
    assert Int(125).round(Int(-2)) == Int(100)


def test_round_accepts_poop_none() -> None:
    from poop.types.none import none

    assert Int(5).round(none) == Int(5)


def test_bit_count() -> None:
    assert Int(0b1011).bit_count() == Int(3)


def test_bit_length() -> None:
    assert Int(8).bit_length() == Int(4)


def test_is_integer_always_true() -> None:
    assert Int(42).is_integer() is true


def test_int_constructor_identity() -> None:
    from poop.transformers.int import _poop_int_from

    n = Int(3)
    assert _poop_int_from(n) is n


def test_float_constructor() -> None:
    from poop.transformers.float import _poop_float_from

    result = _poop_float_from(Int(3))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.0)


def test_complex_constructor() -> None:
    from poop.transformers.complex import _poop_complex_from

    assert _poop_complex_from(Int(3)) == Complex(3 + 0j)


def test_real_returns_self() -> None:
    n = Int(5)
    assert n.real() is n


def test_imag_returns_zero() -> None:
    assert Int(5).imag() == Int(0)


def test_numerator_returns_self() -> None:
    n = Int(7)
    assert n.numerator() is n


def test_denominator_returns_one() -> None:
    assert Int(5).denominator() == Int(1)


def test_conjugate_returns_self() -> None:
    n = Int(5)
    assert n.conjugate() is n


def test_as_integer_ratio() -> None:
    assert Int(5).as_integer_ratio() == Tuple(Int(5), Int(1))


def test_to_bytes_big_endian() -> None:
    assert Int(255).to_bytes(Int(2), Str("big")) == Bytes(b"\x00\xff")


def test_to_bytes_little_endian() -> None:
    assert Int(255).to_bytes(Int(2), Str("little")) == Bytes(b"\xff\x00")


def test_to_bytes_defaults_to_length_one_big_endian() -> None:
    assert Int(255).to_bytes() == Bytes(b"\xff")


def test_to_bytes_signed() -> None:
    assert Int(-2).to_bytes(Int(2), Str("big"), signed=true) == Bytes(b"\xff\xfe")


def test_bin_returns_binary_string() -> None:
    assert Int(10).bin() == Str("0b1010")


def test_hex_returns_hex_string() -> None:
    assert Int(255).hex() == Str("0xff")


def test_oct_returns_octal_string() -> None:
    assert Int(8).oct() == Str("0o10")


def test_chr_returns_character() -> None:
    assert Int(65).chr() == Str("A")


def test_pow_method() -> None:
    assert Int(2).pow(Int(10)) == Int(1024)


def test_from_bytes_big_endian() -> None:
    assert Int.from_bytes(Bytes(b"\x00\xff"), Str("big")) == Int(255)


def test_from_bytes_little_endian() -> None:
    assert Int.from_bytes(Bytes(b"\xff\x00"), Str("little")) == Int(255)


def test_from_bytes_defaults_to_big_endian() -> None:
    assert Int.from_bytes(Bytes(b"\x00\xff")) == Int(255)


def test_from_bytes_signed() -> None:
    assert Int.from_bytes(Bytes(b"\xff\xfe"), Str("big"), signed=true) == Int(-2)


def test_from_bytes_roundtrips_with_to_bytes() -> None:
    n = Int(12345)
    b = n.to_bytes(Int(4), Str("big"))
    assert Int.from_bytes(b, Str("big")) == n


# --- Cross-POOP-type numeric equality (proposal 86) ---


def test_eq_with_float_same_value() -> None:
    from poop.types.float import Float

    assert Int(1) == Float(1.0)
    assert Int(2) != Float(2.5)


def test_ne_with_float_same_value() -> None:
    from poop.types.float import Float

    assert (Int(1) != Float(1.0)) is false
    assert (Int(2) != Float(2.5)) is true


def test_ne_with_non_numeric_returns_true() -> None:
    assert (Int(5) != Str("5")) is true


def test_arith_with_float_operand_promotes_to_float() -> None:
    from poop.types.float import Float

    for op, expected_val in [
        (Int(1) + Float(2.5), 3.5),
        (Int(5) - Float(2.0), 3.0),
        (Int(3) * Float(2.0), 6.0),
        (Int(5) // Float(2.0), 2.0),
        (Int(5) % Float(2.0), 1.0),
    ]:
        assert isinstance(op, Float)
        assert op == Float(expected_val)


def test_pow_with_modulus() -> None:
    # 3-arg modular exponentiation (proposal 83).
    assert Int(5).pow(Int(3), Int(7)) == Int(6)
    assert Int(2).__pow__(Int(10), Int(1000)) == Int(24)


def test_ordering_with_foreign_operand_raises_typeerror() -> None:
    # Proposal 164: ordering a foreign operand must answer CPython's TypeError,
    # not leak an AttributeError from a missing `other._value`.
    with pytest.raises(TypeError):
        _ = Int(2) < Str("x")
    with pytest.raises(TypeError):
        _ = Int(2) >= Tuple(Int(1))


def test_equality_folds_boolean_as_int() -> None:
    # Proposal 165: bool is an int subclass, so Int compares against Booleans.
    assert Int(1) == true
    assert Int(0) == false
    assert (Int(1) != true) is false
    assert Int(2) != true


def test_ordering_with_boolean_operand() -> None:
    # Proposal 165: `Int(0) < True` is True (0 < 1).
    assert Int(0) < true
    assert Int(2) > true


_BAD: Any = List(Int(1), Int(2))


@pytest.mark.parametrize(
    "call, exc",
    [
        pytest.param(
            lambda: Int(5).to_bytes(_BAD, Str("big")), TypeError, id="to_bytes_length"
        ),
        pytest.param(
            lambda: Int(5).to_bytes(Int(2), _BAD), TypeError, id="to_bytes_byteorder"
        ),
        pytest.param(
            lambda: Int.from_bytes(Bytes(b"\x01"), _BAD),
            TypeError,
            id="from_bytes_byteorder",
        ),
        pytest.param(lambda: Int(5).pow(Int(2), _BAD), TypeError, id="pow_modulus"),
        pytest.param(lambda: Int(5).round(_BAD), TypeError, id="round"),
    ],
)
def test_int_wrong_type_arg_is_faithful_not_value_leak(call, exc) -> None:
    # proposals.md item 9: a mandatory argument that carries no `_value` (a
    # List) must reach the underlying Python method raw and raise the faithful
    # exception, never leak the internal `#_value` name through dispatch.
    with pytest.raises(exc) as info:
        call()
    message = str(info.value)
    assert "_value" not in message
    assert "does not understand" not in message


def test_reflected_shift_folds_boolean_on_the_left() -> None:
    # Boolean defines no __lshift__/__rshift__, so `<bool> << Int` resolves to
    # Int's reflected shift, folding the bool to 1/0 (bool is an int subclass).
    assert true << Int(5) == Int(32)
    assert true >> Int(1) == Int(0)
    assert false << Int(4) == Int(0)


def test_reflected_shift_notimplemented_for_foreign_operand() -> None:
    assert Int(5).__rlshift__("x") is NotImplemented
    assert Int(5).__rrshift__(Float(2.0)) is NotImplemented


def test_reflected_bitwise_folds_integral_on_the_left() -> None:
    # CPython's int defines __rand__/__ror__/__rxor__ for symmetry; POOP mirrors
    # them so a reflected `<integral> OP Int` folds the operand to its raw int.
    assert Int(0b0110).__rand__(true) == Int(0b0000)
    assert Int(0b0110).__ror__(true) == Int(0b0111)
    assert Int(0b0110).__rxor__(true) == Int(0b0111)


def test_reflected_bitwise_notimplemented_for_foreign_operand() -> None:
    assert Int(5).__rand__("x") is NotImplemented
    assert Int(5).__ror__(Float(2.0)) is NotImplemented
    assert Int(5).__rxor__("x") is NotImplemented


def test_pow_negative_exponent_returns_float() -> None:
    # 2 ** -1 == 0.5: an int base with a negative exponent yields a Float.
    result = Int(2) ** Int(-1)
    assert isinstance(result, Float)
    assert result._value == pytest.approx(0.5)


def test_from_bytes_takes_an_iterable_of_ints() -> None:
    # `int.from_bytes([1, 2])` is 258 in CPython — the source may be any
    # iterable of ints, which a List of `Int` now is, `Int` answering
    # `__index__`.
    source: Any = List(Int(1), Int(2))  # CPython takes any iterable of ints
    assert Int.from_bytes(source, Str("big")) == Int(258)


def test_int_answers_the_index_protocol() -> None:
    # An Int *is* an index, so no call site has to unwrap `i._value` by hand.
    assert [10, 20, 30][Int(1)] == 20
    assert Int(2).__index__() == 2


def test_pow_with_a_non_int_modulus_names_the_modulus() -> None:
    # CPython's three-operand form names all three — `unsupported operand
    # type(s) for ** or pow(): 'int', 'int', 'str'` — a shape no rewording of
    # the binary message reaches.
    # Deliberately ill-typed: the point is what a program is told when it
    # writes this, and `ty` is right that it should not.
    modulus: Any = Str("a")
    with pytest.raises(TypeError, match=r"^pow's modulus must be an int, got a str$"):
        Int(2).pow(Int(3), modulus)


def test_max_and_min_read_a_none_key_as_absent() -> None:
    # `key=None` is CPython's own default spelling; POOP's `None` is a
    # NoneClass instance, which `is None` read as a comparison block.
    assert Int(5).max(Int(3), key=none) == Int(5)
    assert Int(5).min(Int(3), key=none) == Int(3)


def test_pow_completes_the_reflected_protocol_for_a_complex() -> None:
    # `__pow__` answers NotImplemented for a Complex *on purpose*, so `**`
    # falls through to `Complex.__rpow__`. The message refused where the
    # operator computed — narrower than `**` and than the builtin it replaces.
    assert Int(2).pow(Complex(complex(1, 1))) == Int(2) ** Complex(complex(1, 1))


def test_pow_with_a_modulus_does_not_reflect() -> None:
    # The three-argument form has no reflected counterpart in CPython either.
    with pytest.raises(TypeError, match="does not understand #pow"):
        Int(2).pow(Complex(complex(1, 1)), Int(5))


def test_pow_refusal_names_the_message_not_the_operator() -> None:
    with pytest.raises(TypeError, match=r"int does not understand #pow with a str"):
        Int(2).pow("x")
