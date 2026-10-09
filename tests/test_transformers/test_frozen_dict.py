from functools import partial

import pytest

from poop import Interpreter
from poop.errors import ExecutionError
from poop.transformers.frozen_dict import FrozenDictTransformer, _poop_frozendict_from
from poop.types.dict import Dict
from poop.types.frozen_dict import FrozenDict
from poop.types.int import Int
from poop.types.list import List
from poop.types.tuple import Tuple
from tests._support import rewritten

_rewritten = partial(rewritten, FrozenDictTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("frozendict(x)", "_poop_frozendict_from(x)"),
        ("frozendict()", "_poop_frozendict_from()"),
        ("frozendict(a=1)", "_poop_frozendict_from(a=1)"),
        ("x.frozendict()", "x.frozendict()"),
        # The `**` fold is the dict's, frozen by one more call around it.
        (
            "frozendict(d, **e)",
            "_poop_frozendict_from(_poop_dict_merge(_poop_dict_from(d), e))",
        ),
        # The literal is a dict's, and stays one here.
        ("{'a': 1}", "{'a': 1}"),
    ],
    ids=[
        "call",
        "call_no_arg",
        "keywords",
        "method_named_frozendict",
        "splat",
        "literal",
    ],
)
def test_frozendict_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_poop_frozendict_from() -> None:
    assert (
        FrozenDictTransformer.BINDINGS["_poop_frozendict_from"] is _poop_frozendict_from
    )


def test_frozendict_from_no_arg_is_empty() -> None:
    result = _poop_frozendict_from()
    assert isinstance(result, FrozenDict)
    assert result.len() == Int(0)


def test_frozendict_from_an_exact_frozendict_answers_it() -> None:
    # `frozendict(fd) is fd`, as `frozenset(fs) is fs`.
    fd = _poop_frozendict_from()
    assert _poop_frozendict_from(fd) is fd


def test_frozendict_from_a_dict_copies_it() -> None:
    d = Dict()
    d.at_put(Int(1), Int(2))
    fd = _poop_frozendict_from(d)
    d.at_put(Int(3), Int(4))
    assert str(fd) == "frozendict({1: 2})"


def test_frozendict_from_pairs_and_keywords() -> None:
    fd = _poop_frozendict_from(List(Tuple(Int(1), Int(2))), b=Int(3))
    assert str(fd) == "frozendict({1: 2, 'b': 3})"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("frozendict(5)", "cannot convert int to frozendict"),
        ("frozendict([1])", "cannot use int as frozendict entry"),
        (
            "frozendict([(1, 2, 3)])",
            "frozendict entry must have exactly 2 elements, got 3",
        ),
        (
            "frozendict({}, {})",
            "frozendict is built from at most one mapping or sequence of pairs, "
            "got 2 arguments",
        ),
    ],
    ids=["scalar", "non_pair", "long_pair", "two_arguments"],
)
def test_a_bad_construction_is_refused_under_its_own_name(
    source: str, message: str
) -> None:
    # The refusals are `dict`'s, worded for the constructor the program wrote.
    with pytest.raises(ExecutionError, match=message):
        Interpreter().run_source(source)


def test_end_to_end_splats_and_subclasses(capsys: pytest.CaptureFixture[str]) -> None:
    Interpreter().run_source(
        "fd = frozendict({'a': 1}, b=2)\n"
        "{**fd}.print()\n"
        "(lambda **kw: kw)(**fd).print()\n"
        "dict(fd).print()\n"
        "frozendict(fd, **{'c': 3}).print()\n"
        "class Config(frozendict):\n"
        "    pass\n"
        "Config({'a': 1}).print()\n"
        "Config({'a': 1}).class_name().print()\n"
    )
    assert capsys.readouterr().out == (
        "{'a': 1, 'b': 2}\n"
        "{'a': 1, 'b': 2}\n"
        "{'a': 1, 'b': 2}\n"
        "frozendict({'a': 1, 'b': 2, 'c': 3})\n"
        "frozendict({'a': 1})\n"
        "Config\n"
    )
