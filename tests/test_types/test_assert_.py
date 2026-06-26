import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str


def test_assert_true_returns_self() -> None:
    assert true.assert_(Str("msg")) is true


def test_assert_true_no_message_returns_self() -> None:
    assert true.assert_() is true


def test_assert_false_raises_assertion_error() -> None:
    with pytest.raises(AssertionError, match="x must be positive"):
        false.assert_(Str("x must be positive"))


def test_assert_false_no_message_raises_empty() -> None:
    with pytest.raises(AssertionError, match="^$"):
        false.assert_()


def test_assert_chains_after_comparison() -> None:
    result = (Int(5) > Int(0)).assert_(Str("must be positive"))
    assert result is true


def test_assert_false_from_comparison_raises() -> None:
    with pytest.raises(AssertionError):
        (Int(0) > Int(5)).assert_(Str("must be positive"))


def test_assert_truthy_int_returns_self() -> None:
    five = Int(5)
    assert five.assert_(Str("nonzero")) is five


def test_assert_zero_int_raises() -> None:
    with pytest.raises(AssertionError, match="must be nonzero"):
        Int(0).assert_(Str("must be nonzero"))


def test_assert_nonempty_str_returns_self() -> None:
    s = Str("hi")
    assert s.assert_() is s


def test_assert_empty_str_raises() -> None:
    with pytest.raises(AssertionError, match="must not be empty"):
        Str("").assert_(Str("must not be empty"))


def test_assert_nonempty_list_returns_self() -> None:
    items = List(Int(1))
    assert items.assert_() is items


def test_assert_empty_list_raises() -> None:
    with pytest.raises(AssertionError):
        List().assert_()


def test_assert_none_raises() -> None:
    with pytest.raises(AssertionError, match="not none"):
        none.assert_(Str("not none"))


def test_assert_false_with_poop_none_message_raises_empty() -> None:
    # POOP's NoneTransformer rewrites every `None` literal to the `none`
    # singleton, so `x.assert_(None)` reaches here as a NoneClass. It must be
    # treated as "no message" (bare AssertionError), not crash on `._value`.
    with pytest.raises(AssertionError, match="^$"):
        false.assert_(none)
