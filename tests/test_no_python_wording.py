"""No failure a program can reach describes a construct POOP forbids.

The rewordings live in nine wrappers, two transformers and one translation
step, and each was verified where it was written. This is the test that says
they add up: it runs failing programs end to end, through the same path a user
sees, and refuses the phrases that name Python's constructs rather than POOP's
messages.

A per-site assertion cannot do this — the next wrapper is free to reintroduce
any of them, which is how the ten proposals accumulated in the first place.
"""

import re

import pytest

from poop import Interpreter
from poop.errors import PoopError

# Each pattern names a construct POOP does not have. `indices` and `index out
# of range` describe subscripting (no_subscript); `operand type(s)` and `not
# supported between instances` describe an operator as a type-level protocol
# rather than a message; `<lambda>` and `positional argument` describe a
# block as a Python function; `word()` is a method spelt as a call.
_FORBIDDEN = {
    "subscripting": re.compile(r"indices|index out of range|out of bounds"),
    "operator-as-protocol": re.compile(
        r"operand type\(s\)|not supported between instances"
    ),
    "a block as a function": re.compile(r"<lambda>|positional argument"),
    "a message as a call": re.compile(r"\b\w+\(\)|\b\w+\.\w+\("),
    "a banned dunder": re.compile(r"__\w+__"),
    "a generator": re.compile(r"\bgenerator\b|\byield\b"),
}

# Programs whose failure a reader is meant to understand. Kept as source, not
# as calls into the types, so the assertion covers the whole path — including
# `_describe`, which is where the operator translation runs.
_FAILING = [
    '"abc".at(10)',
    '"abc".at("x")',
    "[1, 2].at(9)",
    '[1, 2].at("x")',
    "(1, 2).at(9)",
    'b"ab".at(9)',
    'bytearray(b"ab").at(9)',
    "range(3).at(9)",
    'memoryview(b"ab").at(9)',
    '{"a": 1}.at("b")',
    "[].pop()",
    "[1, 2].pop(9)",
    "[1, 2].index(9)",
    "(1, 2).index(9)",
    "range(5).index(9)",
    "[1, 2].remove(9)",
    # The six removals: `popitem()`, `pop from …` and `bytearray` are exactly
    # what this sweep is for, and three answered a bare repr with no sentence.
    '{"a": 1}.pop("b")',
    "{}.popitem()",
    "{1}.remove(2)",
    "set().pop()",
    "bytearray().pop()",
    'bytearray(b"a").remove(98)',
    '"abc".slice(slice("a", 2))',
    '[1, 2].slice(slice("a", 2))',
    'int("abc")',
    'float("abc")',
    'int("ff", 99)',
    "[].min()",
    "[].max()",
    "[1, 2].zip([1], strict=True).do(lambda p: p.print())",
    '[1, "a"].sorted()',
    '[1, "a"].min()',
    '[1, "a"].max()',
    '("a" + 1)',
    '(1 + "a")',
    '(1 < "a")',
    "([1] + 1)",
    '(2 ** "a")',
    '(5).divmod("a")',
    "b = lambda x: x\nb(1, 2)",
    # PEP 479 turned this into `generator raised StopIteration` — a report
    # about a construct POOP does not have and no_yield bans.
    "i = [1].iter()\nlist([1, 2, 3].map(lambda v: i.next()))",
    "i = [1].iter()\nlist([1, 2, 3].filter(lambda v: i.next()))",
    "i = [1].iter()\ni.next()\ni.next()",
    "b = lambda: 1\nb(9)",
    # A receiver that cannot be entered, and one that can be entered but never
    # exited: CPython names the missing dunder in both.
    "With(lambda: 5).do(lambda x: x)",
    "class C(Object):\n    def __enter__(self):\n        return 1\n"
    "With(lambda: C()).do(lambda x: x)",
]


def _failure(source: str) -> str:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source)
    return str(info.value)


@pytest.mark.parametrize("source", _FAILING)
def test_no_failure_names_a_forbidden_construct(source: str) -> None:
    message = _failure(source)
    named = [
        construct
        for construct, pattern in _FORBIDDEN.items()
        if pattern.search(message)
    ]
    assert named == [], f"{source!r} answered {message!r}, naming {named}"


@pytest.mark.parametrize("source", _FAILING)
def test_every_failure_still_says_something(source: str) -> None:
    """Guards the sweep: an empty message passes every pattern above."""
    message = _failure(source).split(": ", 1)[-1]
    assert len(message.split()) >= 3


def test_the_sweep_would_catch_a_regression() -> None:
    """The patterns are not vacuous — CPython's own wording trips them."""
    leaked = "TypeError: unsupported operand type(s) for +: 'str' and 'int'"
    assert _FORBIDDEN["operator-as-protocol"].search(leaked)
    assert _FORBIDDEN["subscripting"].search("IndexError: list index out of range")
    assert _FORBIDDEN["a message as a call"].search("list.index(x): x not in list")
