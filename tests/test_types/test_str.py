import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.string import Str


def test_str_wraps_value() -> None:
    assert str(Str("hello")) == "hello"


def test_size() -> None:
    assert Str("hello").size() == Int(5)


def test_size_empty() -> None:
    assert Str("").size() == Int(0)


def test_at_returns_char() -> None:
    assert Str("hello").at(Int(0)) == Str("h")


def test_at_last_char() -> None:
    assert Str("hello").at(Int(4)) == Str("o")


def test_at_out_of_bounds_raises() -> None:
    with pytest.raises(IndexError):
        Str("hello").at(Int(10))


def test_includes_found() -> None:
    assert Str("hello").includes(Str("e")) is true


def test_includes_not_found() -> None:
    assert Str("hello").includes(Str("z")) is false


def test_reversed() -> None:
    assert Str("hello").reversed() == Str("olleh")


def test_reversed_empty() -> None:
    assert Str("").reversed() == Str("")


def test_add_concatenates() -> None:
    assert Str("hello") + Str(" world") == Str("hello world")


def test_eq_same() -> None:
    assert Str("hello") == Str("hello")


def test_eq_different() -> None:
    assert (Str("hello") == Str("world")) is false


def test_ne() -> None:
    assert (Str("hello") != Str("world")) is true


def test_hash_consistent() -> None:
    assert hash(Str("hello")) == hash(Str("hello"))


def test_str_repr_delegates() -> None:
    s = Str("hi")
    assert repr(s) == str(s)
