from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.boolean import false as false2
from poop.types.boolean import true as true2
from poop.types.none import none
from poop.types.string import Str


def test_true_is_instance_of_boolean() -> None:
    assert isinstance(true, Boolean)


def test_class_name_answers_bool() -> None:
    assert true.class_name() == Str("bool")
    assert false.class_name() == Str("bool")


def test_false_is_instance_of_boolean() -> None:
    assert isinstance(false, Boolean)


def test_true_is_singleton() -> None:
    assert true is true2


def test_false_is_singleton() -> None:
    assert false is false2


def test_true_is_not_false() -> None:
    assert true is not false


def test_if_true_calls_block_on_true() -> None:
    result = true.if_true(lambda: 42)
    assert result == 42


def test_if_true_returns_none_on_false() -> None:
    assert false.if_true(lambda: 42) is none


def test_if_false_calls_block_on_false() -> None:
    result = false.if_false(lambda: 42)
    assert result == 42


def test_if_false_returns_none_on_true() -> None:
    assert true.if_false(lambda: 42) is none


def test_if_true_if_false_selects_true_branch() -> None:
    result = true.if_true_if_false(lambda: "yes", lambda: "no")
    assert result == "yes"


def test_if_true_if_false_selects_false_branch() -> None:
    result = false.if_true_if_false(lambda: "yes", lambda: "no")
    assert result == "no"


def test_if_false_if_true_selects_true_branch() -> None:
    result = true.if_false_if_true(lambda: "no", lambda: "yes")
    assert result == "yes"


def test_if_false_if_true_selects_false_branch() -> None:
    result = false.if_false_if_true(lambda: "no", lambda: "yes")
    assert result == "no"


def test_and_lazy_true_evaluates_block() -> None:
    result = true.and_(lambda: false)
    assert result is false


def test_and_lazy_false_does_not_evaluate_block() -> None:
    called = []
    false.and_(lambda: called.append(1) or true)
    assert called == []


def test_or_lazy_false_evaluates_block() -> None:
    result = false.or_(lambda: true)
    assert result is true


def test_or_lazy_true_does_not_evaluate_block() -> None:
    called = []
    true.or_(lambda: called.append(1) or false)
    assert called == []


def test_not_true_returns_false() -> None:
    assert true.not_() is false


def test_not_false_returns_true() -> None:
    assert false.not_() is true


def test_xor_true_true() -> None:
    assert true.xor(true) is false


def test_xor_true_false() -> None:
    assert true.xor(false) is true


def test_xor_false_true() -> None:
    assert false.xor(true) is true


def test_xor_false_false() -> None:
    assert false.xor(false) is false


def test_eqv_true_true() -> None:
    assert true.eqv(true) is true


def test_eqv_true_false() -> None:
    assert true.eqv(false) is false


def test_eqv_false_true() -> None:
    assert false.eqv(true) is false


def test_eqv_false_false() -> None:
    assert false.eqv(false) is true


def test_eager_and_operator() -> None:
    assert (true & false) is false
    assert (true & true) is true
    assert (false & true) is false
    assert (false & false) is false


def test_eager_or_operator() -> None:
    assert (true | false) is true
    assert (true | true) is true
    assert (false | true) is true
    assert (false | false) is false


def test_bitwise_with_int_folds_to_int_wrapper() -> None:
    # `bool` is an int subclass: `True & 5 == 1`, `True | 5 == 5`,
    # `True ^ 5 == 4`, all yielding an int (POOP `Int`), never a raw int.
    from poop.types.int import Int

    for result, expected, label in [
        (true & Int(5), 1, "and"),
        (Int(5) & true, 1, "rand"),
        (true | Int(5), 5, "or"),
        (Int(5) | true, 5, "ror"),
        (true ^ Int(5), 4, "xor"),
        (Int(5) ^ true, 4, "rxor"),
        (false & Int(7), 0, "and-false"),
    ]:
        assert isinstance(result, Int), label
        assert result == Int(expected), label
        assert type(result).__name__ == "int", label


def test_shift_between_booleans_folds_to_int() -> None:
    # A shift has no boolean-algebra reading, so it folds whatever the other
    # operand is: `True << True` is `2` in CPython, an int and not a bool.
    # The mixed cases already worked through `Int`'s reflected side; only
    # Boolean-against-Boolean reached neither operand.
    from poop.types.int import Int

    for result, expected, label in [
        (true << true, 2, "lshift"),
        (true >> true, 0, "rshift"),
        (true << false, 1, "lshift-false"),
        (false << true, 0, "lshift-from-false"),
        (true << Int(3), 8, "lshift-int"),
        (Int(5) << true, 10, "rlshift-int"),
        (true >> Int(1), 0, "rshift-int"),
        (Int(5) >> true, 2, "rrshift-int"),
    ]:
        assert isinstance(result, Int), label
        assert result == Int(expected), label
        assert type(result).__name__ == "int", label


def test_bitwise_between_booleans_stays_boolean() -> None:
    # Two Booleans keep boolean algebra and return the singletons,
    # mirroring CPython's `True & False is False`.
    assert (true ^ false) is true
    assert (true ^ true) is false
    assert (false ^ true) is true
    assert (false ^ false) is false


def test_bool_true() -> None:
    assert bool(true) is True


def test_bool_false() -> None:
    assert bool(false) is False


def test_str_true() -> None:
    assert str(true) == "True"


def test_str_false() -> None:
    assert str(false) == "False"


def test_repr_delegates_to_str() -> None:
    assert repr(true) == str(true)
    assert repr(false) == str(false)


def test_true_is_hashable() -> None:
    assert hash(true) == hash(True)


def test_false_is_hashable() -> None:
    assert hash(false) == hash(False)


def test_true_is_none_returns_false() -> None:
    assert true.is_none() is false


def test_true_not_none_returns_true() -> None:
    assert true.not_none() is true


def test_false_is_none_returns_false() -> None:
    assert false.is_none() is false


def test_false_not_none_returns_true() -> None:
    assert false.not_none() is true


def test_false_lt_true() -> None:
    assert (false < true) is true


def test_true_lt_false_returns_false() -> None:
    assert (true < false) is false


def test_true_eq_true_via_le() -> None:
    assert (true <= true) is true


def test_true_gt_false() -> None:
    assert (true > false) is true


def test_false_ge_false() -> None:
    assert (false >= false) is true


def test_to_boolean_truthy_returns_true_singleton() -> None:
    assert to_boolean(1) is true


def test_to_boolean_falsy_returns_false_singleton() -> None:
    assert to_boolean(0) is false


def test_to_boolean_accepts_poop_boolean() -> None:
    assert to_boolean(true) is true
    assert to_boolean(false) is false


# Arithmetic — bool behaves as int 1/0 (proposal 160)


def test_add_with_int() -> None:
    from poop.types.int import Int

    assert true + Int(1) == Int(2)
    assert Int(1) + true == Int(2)


def test_add_two_booleans() -> None:
    from poop.types.int import Int

    assert true + true == Int(2)
    assert true + false == Int(1)


def test_mul_with_int() -> None:
    from poop.types.int import Int

    assert true * Int(3) == Int(3)
    assert Int(3) * true == Int(3)
    assert false * Int(3) == Int(0)


def test_sub_with_int() -> None:
    from poop.types.int import Int

    assert true - Int(1) == Int(0)
    assert Int(3) - true == Int(2)


def test_truediv_with_int() -> None:
    from poop.types.float import Float
    from poop.types.int import Int

    assert true / Int(2) == Float(0.5)


def test_mod_with_int() -> None:
    from poop.types.int import Int

    assert Int(10) % true == Int(0)


def test_pow_with_int() -> None:
    from poop.types.int import Int

    assert true ** Int(3) == Int(1)
    assert Int(2) ** true == Int(2)


def test_add_with_float() -> None:
    from poop.types.float import Float

    assert true + Float(1.5) == Float(2.5)
    assert Float(1.0) + true == Float(2.0)


def test_sum_of_booleans_counts_truthy() -> None:
    from poop.types.int import Int
    from poop.types.list import List

    assert List(true, false, true, true).sum() == Int(3)


def test_arithmetic_with_foreign_type_raises() -> None:
    import pytest

    with pytest.raises(TypeError):
        _ = true + Str("x")


def test_comparison_with_numeric_tower_folds_as_int() -> None:
    # Proposal 165: bool is an int subclass — a Boolean orders/compares as 1/0
    # against the whole numeric tower, not just against other Booleans.
    from poop.types.float import Float
    from poop.types.int import Int

    assert true > Float(0.5)
    assert (false > Float(0.5)) is false
    assert true == Int(1)
    assert false == Int(0)
    assert (true == false) is false
    assert true == true2
    assert Int(1) == true  # reflected direction


def test_comparison_with_foreign_type() -> None:
    # Equality answers false/true for a foreign operand; ordering raises.
    import pytest

    assert (true == Str("x")) is false
    assert true != Str("x")
    with pytest.raises(TypeError):
        _ = true < Str("x")


def test_floordiv_with_int() -> None:
    from poop.types.int import Int

    assert true // Int(2) == Int(0)
    assert true // Int(1) == Int(1)


def test_forward_mod_with_int() -> None:
    from poop.types.int import Int

    assert true % Int(2) == Int(1)
    assert false % Int(3) == Int(0)


def test_reflected_ops_fold_to_one_and_redispatch() -> None:
    # A left operand that delegates to Boolean's reflected op finds the bool
    # folded to 1 and re-dispatched through Int (bool is an int subclass).
    from poop.types.float import Float
    from poop.types.int import Int

    assert true.__rtruediv__(Int(4)) == Float(4.0)
    assert true.__rfloordiv__(Int(7)) == Int(7)
    assert true.__rand__(Int(0b0110)) == Int(0)
    assert true.__ror__(Int(0b0110)) == Int(0b0111)
    assert true.__rxor__(Int(0b0110)) == Int(0b0111)
    # The shift pair has no expression that reaches it any more — `Boolean`
    # answers the forward operator for both rungs now — but the protocol has
    # two halves and a one-sided one is the next reader's trap.
    assert true.__rlshift__(Int(5)) == Int(10)
    assert true.__rrshift__(Int(5)) == Int(2)


def test_reflected_op_with_operand_lacking_the_method_is_notimplemented() -> None:
    # `none` answers no arithmetic dunder, so Boolean's reflected fallback
    # yields NotImplemented and CPython raises its faithful TypeError.
    import pytest

    from poop.types.none import none

    assert true.__radd__(none) is NotImplemented
    with pytest.raises(TypeError):
        _ = none + true


def test_boolean_answers_the_index_protocol() -> None:
    # bool is an int subclass in CPython: [10, 20][True] is 20.
    assert [10, 20][true] == 20
    assert [10, 20][false] == 10
    assert true.__index__() == 1
    assert false.__index__() == 0


# the int-side messages — proposal 25


def test_the_int_side_messages_answer_what_cpython_answers() -> None:
    # `bool` computes like an `int` in CPython, and every validator naming a
    # numeric substitute (`no_abs` → `x.abs()`, `no_bin` → `x.bin()`, …) left
    # a Boolean receiver with nowhere to go.
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.tuple import Tuple

    assert true.abs() == Int(1)
    assert true.bit_length() == Int(1)
    assert false.bit_count() == Int(0)
    assert true.bit_invert() == Int(-2)
    assert true.negated() == Int(-1)
    assert true.divmod(Int(2)) == Tuple(Int(0), Int(1))
    assert true.pow(Int(2)) == Int(1)
    assert true.round() == Int(1)
    assert true.ceil() == Int(1)
    assert true.floor() == Int(1)
    assert true.trunc() == Int(1)
    assert true.bin() == Str("0b1")
    assert true.hex() == Str("0x1")
    assert true.oct() == Str("0o1")
    assert true.chr() == Str("\x01")
    assert true.to_bytes() == Bytes(b"\x01")
    assert true.as_integer_ratio() == Tuple(Int(1), Int(1))
    assert true.is_integer() is true
    assert true.real() == Int(1)
    assert true.imag() == Int(0)
    assert true.numerator() == Int(1)
    assert true.denominator() == Int(1)
    assert true.conjugate() == Int(1)


def test_from_bytes_completes_the_to_bytes_pair() -> None:
    # The one half-pair in the int-side family: `to_bytes` answered and
    # `from_bytes` did not, with the near-miss hint pointing back at the
    # message the reader had not asked for.
    from poop.types.bytes import Bytes

    assert Boolean.from_bytes(Bytes(b"\x01"), Str("big")) is true
    assert Boolean.from_bytes(Bytes(b"\x00"), Str("big")) is false


def test_from_bytes_answers_a_boolean_because_cpython_runs_it_through_cls() -> None:
    # Unlike `abs` and its neighbours, this one is not a fold: CPython builds
    # the answer through `cls`, so `bool.from_bytes(b"\x05", "big")` is `True`
    # and not `5`.
    from poop.types.bytes import Bytes

    assert Boolean.from_bytes(Bytes(b"\x05"), Str("big")) is true


def test_the_int_side_messages_answer_an_int_not_a_boolean() -> None:
    # `abs(True)` is `1`, not `True`; answering a Boolean would be a quiet
    # type error one message down the chain.
    from poop.types.int import Int

    assert isinstance(true.abs(), Int)
    assert isinstance(true.real(), Int)
    assert true.abs().class_name() == Str("int")


def test_min_and_max_answer_the_operand_cpython_answers() -> None:
    # These two are not folded through `_as_int`: they answer one of their
    # *operands*, and CPython's `min(True, 5)` is `True`.
    from poop.types.int import Int

    assert true.min(Int(5)) is true
    assert true.max(Int(5)) == Int(5)
    assert false.max(true) is true
    assert true.min(Int(5), Int(0)) == Int(0)


def test_min_takes_key_only_by_keyword() -> None:
    import pytest

    from poop.types.int import Int

    with pytest.raises(TypeError):
        true.min(Int(5), lambda n: n)  # ty: ignore[invalid-argument-type]


def test_a_boolean_formats_as_the_int_it_stands_for() -> None:
    # `bool` is an `int` subclass in CPython, so `format(True, ">6")` is the
    # padded `1`. A Boolean has no `_value` slot, so `Object.format` fell
    # through to `object.__format__`, which refuses every non-empty spec.
    assert true.format(Str(">6")) == Str("     1")
    assert true.format(Str("d")) == Str("1")
    assert false.format(Str("03d")) == Str("000")


def test_an_empty_spec_still_answers_the_word() -> None:
    # `format(True, "")` is `'True'`, not `'1'` — folding to Int first would
    # have changed the one spelling that already worked.
    assert true.format() == Str("True")
    assert false.format() == Str("False")
    assert true.format(none) == Str("True")


def test_the_two_formatting_paths_agree() -> None:
    # The template path routes through `to_python` and was already right; this
    # is the receiver path catching up.
    assert Str("{:>6}").format(true) == true.format(Str(">6"))
