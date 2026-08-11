import pytest

from poop.types.boolean import false, true
from poop.types.error import Error
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.object import Object
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


# Proposal 56. `class_`, `kind`, `class_name` and `__str__` were transparent;
# `is_instance` asked about the wrapper, so a handler that fired *because* the
# error is a ValueError was told it is not one.
def test_is_instance_answers_for_the_wrapped_exception() -> None:
    e = Error(ValueError("m"))
    assert e.is_instance(MIRRORS["ValueError"]) is true


def test_is_instance_answers_for_an_ancestor_kind() -> None:
    e = Error(ZeroDivisionError("division by zero"))
    assert e.is_instance(MIRRORS["ArithmeticError"]) is true
    assert e.is_instance(MIRRORS["Exception"]) is true


def test_is_instance_answers_false_for_an_unrelated_kind() -> None:
    e = Error(ValueError("m"))
    assert e.is_instance(MIRRORS["TypeError"]) is false


def test_is_instance_is_not_about_the_wrapper() -> None:
    # `Exception` is the discriminator between the two receivers: the wrapped
    # exception is one, and `Error` — which inherits `Object` alone — is not.
    # Asking about the wrapper answered false here; asking the exception
    # answers true.
    e = Error(ValueError("m"))
    assert not isinstance(e, Exception)
    assert e.is_instance(MIRRORS["Exception"]) is true
    # `Object` is true for both receivers, and true for the *right* reason: a
    # mirror is built on `(Exception, Object)`, so the caught exception really
    # does live in the Object tree.
    assert e.is_instance(Object) is true


def test_is_instance_sees_a_user_defined_subclass() -> None:
    class MyErr(MIRRORS["ValueError"]):  # ty: ignore[unsupported-base]
        pass

    e = Error(MyErr("m"))
    assert e.is_instance(MyErr) is true
    assert e.is_instance(MIRRORS["ValueError"]) is true


def test_is_instance_refuses_a_non_class() -> None:
    e = Error(ValueError("m"))
    with pytest.raises(TypeError, match="#is_instance expects a class"):
        e.is_instance(Int(5))  # ty: ignore[invalid-argument-type]


def test_every_message_about_the_class_agrees_with_kind() -> None:
    # The sweep the proposal asks for: `is_instance` was its only survivor.
    e = Error(ValueError("m"))
    kind = e.kind()
    assert e.class_() is kind
    assert e.class_name() == kind.name()
    assert e.is_instance(kind) is true
    assert kind.is_subclass(MIRRORS["Exception"]) is true
