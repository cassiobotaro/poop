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


def test_refusal_names_the_wrapped_class_not_the_wrapper() -> None:
    # The fourth spelling of the leak class_(), class_name() and __str__ close.
    # `Error` is cloaked as `object` — right for the class, since no exception
    # name is true for it, and wrong for an instance that stands for exactly
    # one. Python reports `'ZeroDivisionError' object has no attribute 'zzz'`.
    import pytest

    from poop.types.object import MessageNotUnderstood

    with pytest.raises(MessageNotUnderstood, match="ZeroDivisionError does not"):
        Error(ZeroDivisionError("division by zero")).zzz()  # ty: ignore[unresolved-attribute]


def test_refusal_keeps_every_hint_shape() -> None:
    # The label is the only thing overridden: the typo hint and the Smalltalk
    # selector table must still answer for an Error receiver.
    import pytest

    from poop.types.object import MessageNotUnderstood

    error = Error(ValueError("boom"))
    with pytest.raises(MessageNotUnderstood, match="did you mean #message"):
        error.mesage()  # ty: ignore[unresolved-attribute]
    with pytest.raises(MessageNotUnderstood, match="#printNl is #print here"):
        Error(ValueError("boom")).printNl()  # ty: ignore[unresolved-attribute]


def test_explain_derives_the_label_when_none_is_given() -> None:
    # Only Error passes one; every other receiver keeps naming its own type.
    from poop.types._selectors import explain
    from poop.types.int import Int

    assert explain(Int(1), "zzz").startswith("int does not understand")
