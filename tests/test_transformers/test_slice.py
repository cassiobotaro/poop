from functools import partial

import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.transformers.slice import SliceTransformer, _poop_slice_from
from poop.types.int import Int
from poop.types.slice import Slice
from tests._support import rewritten

_rewritten = partial(rewritten, SliceTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = slice(1, 5)", "x = _poop_slice_from(1, 5)"),
        ("x = slice(0, 10, 2)", "x = _poop_slice_from(0, 10, 2)"),
        # CPython's slice(stop) means slice(None, stop): the lone argument is
        # the stop. The rewrite used to insert the None here, counting
        # argument *nodes* — and a starred argument is one node carrying any
        # number of values. The converter counts the values it receives.
        ("x = slice(5)", "x = _poop_slice_from(5)"),
        ("x = slice(*xs)", "x = _poop_slice_from(*xs)"),
        ("x = myslice(1, 5)", "x = myslice(1, 5)"),
        ("f = slice", "f = _poop_slice_cls"),
    ],
    ids=[
        "call",
        "three_args",
        "one_arg_reaches_the_converter",
        "starred_reaches_the_converter",
        "other_names_untouched",
        "bare_name_to_mangled_binding",
    ],
)
def test_slice_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_the_alias_and_the_converter() -> None:
    # A bare name binds the alias, a subclass of `Slice` whose call converts;
    # a call goes through the converter, which guards the arity. `Slice(...)`
    # *is* the call, so this was the one constructor with no factory at all,
    # and its refusal named `slice.__init__()`.
    alias = SliceTransformer.BINDINGS["_poop_slice_cls"]
    assert isinstance(alias, type) and issubclass(alias, Slice)
    assert "_poop_slice_from" in SliceTransformer.BINDINGS


# The one-argument rule lives in the converter, where the count is of values.


def test_converter_reads_a_lone_argument_as_the_stop() -> None:
    assert _poop_slice_from(Int(5)) == Slice(None, Int(5))


def test_converter_keeps_two_arguments_as_start_and_stop() -> None:
    assert _poop_slice_from(Int(1), Int(5)) == Slice(Int(1), Int(5))


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("slice(5).print()", "slice(None, 5, None)"),
        ("xs = (1, 5)\nslice(*xs).print()", "slice(1, 5, None)"),
        ("xs = (5,)\nslice(*xs).print()", "slice(None, 5, None)"),
    ],
    ids=["literal", "starred_two_values", "starred_one_value"],
)
def test_a_starred_slice_counts_its_values(
    source: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(source)
    assert capsys.readouterr().out.strip() == expected


def test_too_many_arguments_keep_their_refusal() -> None:
    with pytest.raises(PoopError, match="got 4 arguments — write slice"):
        Interpreter().run_source("slice(1, 2, 3, 4)")


# The convert/build gap `_alias.py` closes for every other constructor: a
# bare `slice` named the class, whose `__init__` reads a lone argument as the
# *start*, so `s = slice; s(5)` silently built a different slice than `slice(5)`.


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("s = slice\ns(5).print()", "slice(None, 5, None)"),
        ("class S(slice):\n    pass\nS(5).print()", "slice(None, 5, None)"),
        ("class S(slice):\n    pass\nS(5).class_().name().print()", "S"),
        ("class S(slice):\n    pass\nS(1, 5, 2).print()", "slice(1, 5, 2)"),
    ],
    ids=["rebound_name", "subclass", "subclass_keeps_its_class", "subclass_three"],
)
def test_a_bare_slice_builds_through_the_converter(
    source: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(source)
    assert capsys.readouterr().out.strip() == expected


def test_a_rebound_slice_refuses_four_arguments_as_the_literal_does() -> None:
    with pytest.raises(PoopError, match="got 4 arguments — write slice"):
        Interpreter().run_source("s = slice\ns(1, 2, 3, 4)")
