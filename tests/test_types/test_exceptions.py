import pytest

from poop.interpreter import Interpreter
from poop.types.exceptions import MIRRORS, PoopExcMeta, poop_class_of
from poop.types.object import Object
from poop.types.string import Str

_ValueError = MIRRORS["ValueError"]
_KeyError = MIRRORS["KeyError"]
_LookupError = MIRRORS["LookupError"]
_Exception = MIRRORS["Exception"]


def test_a_mirror_matches_the_native_exception_it_stands_for() -> None:
    # The whole design: Try matches with isinstance(), which is POOP's own
    # code, so __instancecheck__ is enough and no translation layer is needed.
    assert isinstance(ValueError("x"), _ValueError)
    assert isinstance(KeyError("k"), _KeyError)


def test_a_mirror_matches_natives_through_the_hierarchy() -> None:
    assert isinstance(KeyError("k"), _LookupError)
    assert isinstance(IndexError(), _LookupError)
    assert isinstance(ValueError("v"), _Exception)


def test_a_mirror_does_not_over_match() -> None:
    assert not isinstance(KeyError("k"), _ValueError)
    assert not isinstance(ValueError("v"), _KeyError)


def test_a_mirror_is_still_raisable_and_caught_as_its_native() -> None:
    # `raise_` depends on this: it does `raise exc_type(*args)`.
    with pytest.raises(ValueError):
        raise _ValueError("boom")


def test_user_subclass_does_not_inherit_native_and_catch_everything() -> None:
    # The trap: inheriting the root's `_native = Exception` would make
    # except_(MyError, ...) catch every exception in the program.
    class MyError(_Exception):  # ty: ignore[unsupported-base]
        pass

    assert isinstance(MyError("x"), MyError)
    assert not isinstance(ValueError("v"), MyError)
    assert not isinstance(KeyError("k"), MyError)


def test_user_subclass_of_a_mirror_matches_only_itself() -> None:
    class MyValueError(_ValueError):  # ty: ignore[unsupported-base]
        pass

    assert not isinstance(ValueError("v"), MyValueError)
    assert isinstance(MyValueError("x"), _ValueError)


def test_a_user_exception_lands_inside_the_object_tree() -> None:
    # Before this, `class MyError(Exception)` sat outside Object entirely and
    # `MyError("x").class_name()` failed.
    class MyError(_Exception):  # ty: ignore[unsupported-base]
        pass

    assert issubclass(MyError, Object)
    assert MyError("x").class_name() == Str("MyError")


def test_mirrors_answer_the_class_side_protocol() -> None:
    assert _ValueError.name() == Str("ValueError")  # ty: ignore[unresolved-attribute]
    assert _KeyError.superclass() is _LookupError  # ty: ignore[unresolved-attribute]
    assert _ValueError.superclass() is _Exception  # ty: ignore[unresolved-attribute]


def test_poop_class_of_answers_the_mirror_for_a_native() -> None:
    assert poop_class_of(ValueError("v")) is _ValueError


def test_poop_class_of_answers_a_user_exception_itself() -> None:
    class MyError(_Exception):  # ty: ignore[unsupported-base]
        pass

    assert poop_class_of(MyError("x")) is MyError


def test_poop_class_of_never_leaks_an_unmirrored_native() -> None:
    # MemoryError has no mirror; the nearest one answers rather than the raw
    # class escaping back out.
    answered = poop_class_of(MemoryError())
    assert isinstance(answered, PoopExcMeta)
    assert answered is _Exception


def test_every_mirror_is_a_poop_class() -> None:
    for mirror in MIRRORS.values():
        assert isinstance(mirror, PoopExcMeta)
        assert issubclass(mirror, Object)


# --- through the interpreter ---


def test_except_catches_the_raw_valueerror_int_raises() -> None:
    Interpreter().run_source(
        "class P:\n"
        "    def run(self):\n"
        '        Try(lambda: int("abc")).except_(\n'
        "            ValueError, lambda e: e.kind().name()\n"
        "        ).run()\n"
        "P().run()\n"
    )


def test_except_lookup_error_catches_the_raw_keyerror_dict_raises() -> None:
    Interpreter().run_source(
        "class P:\n"
        "    def run(self):\n"
        '        return Try(lambda: {"a": 1}.at("zzz")).except_(\n'
        "            LookupError, lambda e: e.kind().name()\n"
        "        ).run()\n"
        "P().run()\n"
    )


def test_unmatched_exception_is_still_reraised() -> None:
    from poop.errors import ExecutionError

    with pytest.raises(ExecutionError, match="KeyError"):
        Interpreter().run_source(
            "class P:\n"
            "    def run(self):\n"
            '        Try(lambda: {"a": 1}.at("zzz")).except_(\n'
            "            ValueError, lambda e: 0\n"
            "        ).run()\n"
            "P().run()\n"
        )


def test_raise_still_works_after_the_name_is_rewritten() -> None:
    # `raise_` is a class-side message on `PoopExcMeta`, so the mirror this
    # rewrites to answers it — no ordering constraint between the two
    # transformers any more.
    Interpreter().run_source(
        "class P:\n"
        "    def run(self):\n"
        '        Try(lambda: ValueError.raise_("boom")).except_(\n'
        "            ValueError, lambda e: e.message()\n"
        "        ).run()\n"
        "P().run()\n"
    )


def test_poop_class_of_falls_back_to_exception_for_unmirrored_base() -> None:
    # A BaseException subtree with no mirror (KeyboardInterrupt is not under
    # Exception) answers with the root Exception mirror rather than leaking the
    # raw native class back to user code.
    from poop.types.exceptions import MIRRORS, poop_class_of

    assert poop_class_of(KeyboardInterrupt()) is MIRRORS["Exception"]


# `raise_` as a real message — proposal 27


def test_raise_from_a_computed_class() -> None:
    """`RaiseTransformer` matched a literal uppercase Name, so every other way
    of naming the same class answered `does not understand #raise_`."""
    Interpreter().run_source(
        "err = ValueError\n"
        'Try(lambda: err.raise_("boom")).except_(\n'
        "    ValueError, lambda e: e.message()\n"
        ").run()\n"
    )


def test_raise_from_a_class_read_out_of_a_collection() -> None:
    Interpreter().run_source(
        'errors = {"e": ValueError}\n'
        'Try(lambda: errors.at("e").raise_("boom")).except_(\n'
        "    ValueError, lambda e: e.message()\n"
        ").run()\n"
    )


def test_a_handler_can_re_raise_what_it_caught(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The one that matters: `Try` swallows an exception as soon as a handler
    # matches and `raise` is banned, so before this there was no way to
    # re-raise at all.
    Interpreter().run_source(
        "Try(lambda:\n"
        '    Try(lambda: ValueError.raise_("original")).except_(\n'
        "        ValueError, lambda e: e.kind().raise_(e.message())\n"
        "    ).run()\n"
        ').except_(ValueError, lambda e: ("re-raised: " + e.message()).print()).run()\n'
    )
    assert capsys.readouterr().out == "re-raised: original\n"


def test_a_user_error_class_answers_raise() -> None:
    Interpreter().run_source(
        "class MyError(Exception):\n"
        "    pass\n"
        'Try(lambda: MyError.raise_("mine")).except_(\n'
        "    MyError, lambda e: e.message()\n"
        ").run()\n"
    )


def test_a_class_that_is_not_an_error_cannot_be_raised(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The rewrite assumed any capitalized receiver was raisable, so this
    # answered `A() takes no arguments` — the constructor of a class the
    # program never asked to build.
    Interpreter().run_source(
        "class A(Object):\n"
        "    pass\n"
        'Try(lambda: A.raise_("x")).except_(Exception, lambda e: e.message().print())'
        ".run()\n"
    )
    assert "A cannot be raised" in capsys.readouterr().out


def test_raise_carries_keyword_arguments() -> None:
    """An exception whose fields arrive by keyword must still be raisable."""
    Interpreter().run_source(
        "class MyError(Exception):\n"
        "    def __init__(self, message, code):\n"
        "        super().__init__(message)\n"
        "        self.code = code\n"
        'Try(lambda: MyError.raise_("boom", code=42)).except_(\n'
        "    MyError, lambda e: e.message()\n"
        ").run()\n"
    )


def test_the_end_of_input_has_a_mirror() -> None:
    """`Str.input` is the one message that reads from outside the program.

    The reachability argument in this module's docstring was one short: end of
    input needs no files and no modules, only a pipe, and a program could not
    name what it was catching.
    """
    assert "EOFError" in MIRRORS
    assert isinstance(EOFError("x"), MIRRORS["EOFError"])
    assert not isinstance(ValueError("x"), MIRRORS["EOFError"])
    assert MIRRORS["EOFError"].name() == Str("EOFError")  # ty: ignore[unresolved-attribute]


def test_the_unicode_family_is_answered_by_value_error_instead() -> None:
    # Deliberately unmirrored: `UnicodeError` is a ValueError in CPython's own
    # tree, and mirroring it would mean reproducing a five-argument
    # constructor whose __str__ composes the `codec` sentence `_codec.py`
    # exists to keep out.
    assert "UnicodeEncodeError" not in MIRRORS
    assert "UnicodeDecodeError" not in MIRRORS
