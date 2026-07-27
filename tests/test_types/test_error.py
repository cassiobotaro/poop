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


def test_str_names_the_wrapped_class_not_the_wrapper() -> None:
    # `Error` is a poop.types detail user code can neither name nor construct,
    # so it had no business printing itself as `Error(division by zero)`.
    assert str(Error(ZeroDivisionError("division by zero"))) == (
        "ZeroDivisionError: division by zero"
    )


def test_str_of_a_key_error_carries_no_python_quoting() -> None:
    # `KeyError.__str__` answers repr(args[0]), which used to print
    # `Error('z')` — Python's quotes around a POOP string.
    assert str(Error(MIRRORS["KeyError"]("dict has no key 'z'"))) == (
        "KeyError: dict has no key 'z'"
    )


def test_str_of_a_message_less_error_degrades_to_the_bare_name() -> None:
    assert str(Error(AssertionError())) == "AssertionError"
