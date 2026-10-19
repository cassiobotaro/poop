import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter
from poop.types._selectors import explain
from poop.types.boolean import false, true
from poop.types.error import Error
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.object import MessageNotUnderstood, Object
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
    with pytest.raises(MessageNotUnderstood, match="ZeroDivisionError does not"):
        Error(ZeroDivisionError("division by zero")).zzz()


def test_refusal_keeps_every_hint_shape() -> None:
    # The label is the only thing overridden: the typo hint and the Smalltalk
    # selector table must still answer for an Error receiver.
    error = Error(ValueError("boom"))
    with pytest.raises(MessageNotUnderstood, match="did you mean #message"):
        error.mesage()
    with pytest.raises(MessageNotUnderstood, match="#printNl is #print here"):
        Error(ValueError("boom")).printNl()


def test_explain_derives_the_label_when_none_is_given() -> None:
    # Only Error passes one; every other receiver keeps naming its own type.
    assert explain(Int(1), "zzz").startswith("int does not understand")


# `class_`, `kind`, `class_name` and `__str__` were transparent;
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


# `raise_`, `name` and `superclass` are class-side messages the
# mirror genuinely answers, and an `Error` refused all three under that class's
# own name — a sentence `does_not_understand` built by sending `#name` to the
# very class it then said did not understand `#name`.
def test_raise_re_raises_the_very_exception_that_was_caught() -> None:
    original = MIRRORS["ValueError"]("boom")
    error = Error(original)
    with pytest.raises(ValueError) as caught:
        error.raise_()
    # The identity, not merely the kind and the text: `e.kind().raise_(
    # e.message())` built a new exception and dropped notes and traceback.
    assert caught.value is original


def test_raise_keeps_the_notes_a_new_exception_would_drop() -> None:
    original = MIRRORS["ValueError"]("boom")
    # Through `BaseException`: the instance side refuses `add_note` by name.
    BaseException.add_note(original, "context worth keeping")
    with pytest.raises(ValueError) as caught:
        Error(original).raise_()
    assert caught.value.__notes__ == ["context worth keeping"]


@pytest.mark.parametrize("name", ["name", "superclass"])
def test_a_class_side_message_is_refused_by_saying_so(name: str) -> None:
    error = Error(MIRRORS["ValueError"]("m"))
    with pytest.raises(MessageNotUnderstood, match=f"#{name} asks a class"):
        getattr(error, name)


def test_the_redirect_names_the_message_that_answers() -> None:
    error = Error(MIRRORS["ValueError"]("m"))
    with pytest.raises(MessageNotUnderstood, match=r"send it to #kind\(\)"):
        error.name()
    # And the redirect is true: the kind does answer it.
    assert error.kind().name() == Str("ValueError")


def test_an_unknown_name_keeps_the_generic_refusal() -> None:
    error = Error(MIRRORS["ValueError"]("m"))
    with pytest.raises(MessageNotUnderstood, match="try :methods"):
        error.zzz()


def test_a_refusing_class_side_descriptor_is_not_redirected() -> None:
    # `args` is a `class_side_read_refusal`, so the class does not answer it
    # either — pointing at `#kind()` would send the reader to another refusal;
    # the error words it as the class does, naming the message that answers.
    error = Error(MIRRORS["ValueError"]("m"))
    with pytest.raises(MessageNotUnderstood, match="a caught error answers #message"):
        error.args  # noqa: B018


def test_no_mirror_advertises_a_name_a_caught_error_refuses() -> None:
    # The sweep the proposal asks for, now that both halves agree. `raise_` is
    # answered by the error itself; `name` and `superclass` are refused by a
    # sentence that does not claim the kind refuses them.
    for kind, cls in MIRRORS.items():
        error = Error(cls("m"))
        for name in dir(cls):
            if name.startswith("_") or name in {"name", "superclass"}:
                continue
            try:
                getattr(error, name)
            except MessageNotUnderstood:
                pytest.fail(f"{kind}.dir() lists #{name}, which a caught error refuses")


# The state a program's own exception class stored, and identity across a
# re-raise.

_FIELD = (
    "class Field(Exception):\n"
    "    def __init__(self, code):\n"
    "        self.code = code\n"
    '        super().__init__("code")\n'
)


@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        ("lambda e: e.code.print()", "7"),
        ('lambda e: e.has_attr("code").print()', "True"),
        ('lambda e: e.dir().includes("code").print()', "True"),
        ('lambda e: e.get_attr("code").print()', "7"),
    ],
    ids=["read", "has_attr", "dir", "get_attr"],
)
def test_a_caught_error_forwards_the_exceptions_own_state(
    handler: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(
        f"{_FIELD}Try(lambda: Field.raise_(code=7)).except_(Field, {handler}).run()"
    )
    assert capsys.readouterr().out.strip() == expected


def test_a_native_method_is_still_refused_on_a_caught_user_error() -> None:
    with pytest.raises(ExecutionError) as info:
        Interpreter().run_source(
            f"{_FIELD}Try(lambda: Field.raise_(code=7))"
            ".except_(Field, lambda e: e.add_note).run()"
        )
    assert info.value.message == (
        "AttributeError: Field does not understand #add_note — "
        "#add_note is Python's; POOP does not offer it"
    )


def test_a_private_name_stored_on_the_exception_is_not_forwarded() -> None:
    exc = MIRRORS["ValueError"]("m")
    exc.__dict__["_secret"] = 1
    with pytest.raises(MessageNotUnderstood):
        Error(exc)._secret  # noqa: B018


def test_errors_wrapping_one_exception_are_one_error() -> None:
    exc = MIRRORS["ValueError"]("m")
    assert Error(exc) == Error(exc)
    assert Error(exc).hash() == Error(exc).hash()
    assert (Error(exc) == Error(MIRRORS["ValueError"]("m"))) is false


def test_the_re_raised_error_equals_the_one_first_caught(
    capsys: pytest.CaptureFixture[str],
) -> None:
    Interpreter().run_source(
        'e1 = Try(lambda: ValueError.raise_("x")).except_(ValueError, lambda e: e).run()\n'
        "Try(lambda: e1.raise_()).except_(ValueError, lambda e: (e == e1).print()).run()\n"
        "Try(lambda: e1.raise_())"
        ".except_(ValueError, lambda e: (e.hash() == e1.hash()).print()).run()"
    )
    assert capsys.readouterr().out == "True\nTrue\n"


# The chain: `cause()` and `context()`


def _nested(inner_handler: str, outer_handler: str) -> str:
    """A program whose `ZeroDivisionError` handler raises, caught one level out."""
    return (
        "Try(lambda: Try(lambda: 1 / 0)\n"
        f"    .except_(ZeroDivisionError, lambda e: {inner_handler}).run()\n"
        f").except_(KeyError, lambda e: {outer_handler}).run()\n"
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            _nested('KeyError("outer").raise_from(e)', "e.cause().message().print()"),
            "division by zero",
        ),
        (
            _nested(
                'KeyError("outer").raise_from(e)', "e.cause().kind().name().print()"
            ),
            "ZeroDivisionError",
        ),
        (
            'Try(lambda: ValueError.raise_("x"))'
            ".except_(ValueError, lambda e: e.cause().is_none().print()).run()\n",
            "True",
        ),
        (
            _nested('KeyError.raise_("outer")', "e.context().kind().name().print()"),
            "ZeroDivisionError",
        ),
        (
            _nested(
                'KeyError("outer").raise_from(ValueError("inner"))',
                "e.context().is_none().print()",
            ),
            "True",
        ),
        (
            _nested(
                'KeyError("outer").raise_from(None)', "e.cause().is_none().print()"
            ),
            "True",
        ),
        (
            _nested(
                'KeyError("outer").raise_from(None)', "e.context().is_none().print()"
            ),
            "True",
        ),
        (
            "Try(lambda: [1].at(5))"
            ".except_(IndexError, lambda e: e.context().is_none().print()).run()\n",
            "True",
        ),
    ],
    ids=[
        "cause-message",
        "cause-kind",
        "no-cause",
        "context",
        "context-suppressed-by-a-cause",
        "from-none-cause",
        "from-none-context",
        "composed-error-has-no-context",
    ],
)
def test_a_caught_error_answers_its_chain(
    source: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(source)
    assert capsys.readouterr().out == expected + "\n"


def test_a_cause_is_the_error_a_handler_was_given() -> None:
    caught = ValueError("inner")
    outer = KeyError("outer")
    outer.__cause__ = caught
    assert Error(outer).cause() == Error(caught)


def test_raise_on_a_caught_error_refuses_an_argument_in_poops_words() -> None:
    with pytest.raises(ExecutionError) as info:
        Interpreter().run_source(
            'Try(lambda: ValueError.raise_("x"))'
            ".except_(ValueError, lambda e: e.raise_(1)).run()\n"
        )
    assert info.value.message == (
        "TypeError: #raise_ takes no argument on a caught error, got 1 argument"
    )
