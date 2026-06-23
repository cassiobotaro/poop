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
