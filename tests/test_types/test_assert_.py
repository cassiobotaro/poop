import pytest

from poop.types.boolean import false, true


def test_assert_true_returns_self() -> None:
    assert true.assert_("msg") is true


def test_assert_true_no_message_returns_self() -> None:
    assert true.assert_() is true


def test_assert_false_raises_assertion_error() -> None:
    with pytest.raises(AssertionError, match="x must be positive"):
        false.assert_("x must be positive")


def test_assert_false_no_message_raises_empty() -> None:
    with pytest.raises(AssertionError, match="^$"):
        false.assert_()


def test_assert_message_is_stringified() -> None:
    from poop.types.string import Str

    with pytest.raises(AssertionError, match="bad value"):
        false.assert_(Str("bad value"))


def test_assert_chains_after_comparison() -> None:
    from poop.types.int import Int

    result = (Int(5) > Int(0)).assert_("must be positive")
    assert result is true


def test_assert_false_from_comparison_raises() -> None:
    from poop.types.int import Int

    with pytest.raises(AssertionError):
        (Int(0) > Int(5)).assert_("must be positive")
