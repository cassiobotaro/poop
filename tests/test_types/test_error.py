from poop.types.error import Error
from poop.types.string import Str


def test_message_returns_str_with_exception_message() -> None:
    e = Error(ValueError("something went wrong"))
    assert e.message() == Str("something went wrong")


def test_message_returns_str_instance() -> None:
    e = Error(KeyError("missing key"))
    assert isinstance(e.message(), Str)


def test_kind_returns_exception_class_name() -> None:
    e = Error(ValueError("oops"))
    assert e.kind() == Str("ValueError")


def test_kind_returns_str_instance() -> None:
    e = Error(TypeError("bad type"))
    assert isinstance(e.kind(), Str)


def test_str_includes_exception_info() -> None:
    e = Error(RuntimeError("boom"))
    assert "boom" in str(e)


def test_repr_delegates_to_str() -> None:
    e = Error(RuntimeError("boom"))
    assert repr(e) == str(e)


def test_error_wraps_different_exception_types() -> None:
    assert Error(ValueError("v")).kind() == Str("ValueError")
    assert Error(KeyError("k")).kind() == Str("KeyError")
    assert Error(TypeError("t")).kind() == Str("TypeError")
