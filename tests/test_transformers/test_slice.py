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
        ("f = slice", "f = _poop_slice"),
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


def test_bindings_contains_mangled_slice() -> None:
    assert "_poop_slice" in SliceTransformer.BINDINGS
    assert SliceTransformer.BINDINGS["_poop_slice"] is Slice
    # A call goes through the factory, which guards the arity. `Slice(...)`
    # *is* the call, so this was the one constructor with no factory at all, and its refusal named `slice.__init__()`.
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
