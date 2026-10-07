from functools import partial

import pytest

from poop.transformers.slice import SliceTransformer
from poop.types.slice import Slice
from tests._support import rewritten

_rewritten = partial(rewritten, SliceTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = slice(1, 5)", "x = _poop_slice_from(1, 5)"),
        ("x = slice(0, 10, 2)", "x = _poop_slice_from(0, 10, 2)"),
        # CPython's slice(stop) means slice(None, stop): the lone argument is
        # the stop, so the rewrite must insert an implicit None start before it.
        ("x = slice(5)", "x = _poop_slice_from(None, 5)"),
        ("x = myslice(1, 5)", "x = myslice(1, 5)"),
        ("f = slice", "f = _poop_slice"),
    ],
    ids=[
        "call",
        "three_args",
        "one_arg_injects_none_start",
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
