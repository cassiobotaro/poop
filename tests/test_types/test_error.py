from poop.types.error import Error
from poop.types.exceptions import MIRRORS
from poop.types.string import Str


def test_message_returns_str_with_exception_message() -> None:
    e = Error(ValueError("something went wrong"))
    assert e.message() == Str("something went wrong")


def test_message_returns_str_instance() -> None:
    e = Error(KeyError("missing key"))
    assert isinstance(e.message(), Str)


def test_kind_returns_exception_class_name() -> None:
    e = Error(ValueError("oops"))
    assert e.kind().name() == Str("ValueError")


def test_kind_answers_the_poop_class_not_the_native_one() -> None:
    e = Error(TypeError("bad type"))
    assert e.kind() is MIRRORS["TypeError"]
    assert e.kind() is not TypeError


def test_class_name_answers_wrapped_exception_not_error() -> None:
    # Transparent identity: class_name() must not leak the internal `Error`.
    e = Error(IndexError("pop from empty list"))
    assert e.class_name() == Str("IndexError")
    assert e.class_() is MIRRORS["IndexError"]


def test_str_includes_exception_info() -> None:
    e = Error(RuntimeError("boom"))
    assert "boom" in str(e)


def test_repr_delegates_to_str() -> None:
    e = Error(RuntimeError("boom"))
    assert repr(e) == str(e)


def test_error_wraps_different_exception_types() -> None:
    assert Error(ValueError("v")).kind() is MIRRORS["ValueError"]
    assert Error(KeyError("k")).kind() is MIRRORS["KeyError"]
    assert Error(TypeError("t")).kind() is MIRRORS["TypeError"]
