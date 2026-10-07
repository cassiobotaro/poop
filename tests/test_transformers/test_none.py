from functools import partial

import pytest

from poop.transformers.none import NoneTransformer
from poop.types.none import none
from tests._support import rewritten

_rewritten = partial(rewritten, NoneTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [("x = None", "x = _poop_none"), ("x = 42", "x = 42")],
    ids=["none_literal", "other_constants_unchanged"],
)
def test_none_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_none() -> None:
    assert NoneTransformer.BINDINGS["_poop_none"] is none
