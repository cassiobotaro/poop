from functools import partial

import pytest

from poop import Interpreter
from poop.errors import ExecutionError
from poop.transformers.sentinel import SentinelTransformer, _poop_sentinel_from
from poop.types.sentinel import Sentinel
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, SentinelTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('sentinel("X")', "_poop_sentinel_from('X')"),
        ('sentinel("X", repr="<X>")', "_poop_sentinel_from('X', repr='<X>')"),
        ("x.is_instance(sentinel)", "x.is_instance(_poop_sentinel_cls)"),
        ("x.sentinel()", "x.sentinel()"),
    ],
    ids=["call", "keyword", "name", "method_named_sentinel"],
)
def test_sentinel_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_poop_sentinel_from() -> None:
    assert SentinelTransformer.BINDINGS["_poop_sentinel_from"] is _poop_sentinel_from


def test_sentinel_from_builds_a_sentinel() -> None:
    marker = _poop_sentinel_from(Str("M"))
    assert isinstance(marker, Sentinel)
    assert repr(marker) == "M"
    assert repr(_poop_sentinel_from(Str("M"), repr=Str("<M>"))) == "<M>"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("sentinel(5)", "sentinel's name must be a str, got an int"),
        ('sentinel("a", repr=5)', "sentinel's repr must be a str, got an int"),
        # The arity shapes are CPython's, under the cloaked name.
        ("sentinel()", "sentinel\\(\\) missing 1 required positional argument"),
        (
            'sentinel("a", "b")',
            "sentinel\\(\\) takes 1 positional argument but 2 were given",
        ),
    ],
    ids=["name_type", "repr_type", "no_name", "positional_repr"],
)
def test_a_bad_construction_is_refused(source: str, message: str) -> None:
    with pytest.raises(ExecutionError, match=message):
        Interpreter().run_source(source)
