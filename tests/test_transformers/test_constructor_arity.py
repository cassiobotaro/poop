"""A constructor call never resolves to the wrapper class.

Each rewriter used to guard `visit_Call` on the arity its converter could
handle and let anything else fall through to `visit_Name`, which renames the
bare builtin to the *class* binding — and a class constructor is variadic
(`List(*elements)`). So one name meant "convert" at one arity and "build from
these elements" at another, and only the first matched Python:

    list(1, 2).print()   ->  1 2      CPython: list expected at most 1 argument

`list(a, b)` is a plausible slip for `[a, b]`, and CPython exists to catch it.
The scalar wrappers fell through the same way; there the answer was right but
the report named `__init__`, a dunder `no_dunder_attribute` bans outright.
"""

import pytest

from poop import Interpreter
from poop.errors import ExecutionError


def _failure(source: str) -> str:
    with pytest.raises(ExecutionError) as caught:
        Interpreter().run_source(source)
    return str(caught.value)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("list(1, 2)", "list is built from at most one collection, got 2 arguments"),
        ("tuple(1, 2)", "tuple is built from at most one collection, got 2 arguments"),
        ("set(1, 2)", "set is built from at most one collection, got 2 arguments"),
        (
            "frozenset(1, 2)",
            "frozenset is built from at most one collection, got 2 arguments",
        ),
        ("dict(1, 2, 3)", "dict is built from at most one mapping"),
        ("complex(1, 2, 3)", "complex is built from at most a real"),
        ("memoryview(b'ab', 1)", "memoryview is built from exactly one bytes-like"),
        ("bytearray('ab', 'utf-8', 'strict')", "bytearray is built from at most one"),
        ("bytes(b'a', 'utf-8', 'strict')", "bytes is built from at most one source"),
    ],
)
def test_an_over_supplied_constructor_is_refused(source: str, expected: str) -> None:
    assert expected in _failure(source)


@pytest.mark.parametrize(
    "builtin", ["list", "tuple", "set", "frozenset", "memoryview", "bytearray", "bytes"]
)
def test_a_keyword_is_refused_by_the_converter(builtin: str) -> None:
    message = _failure(f"{builtin}(x=1)")
    assert f"{builtin} takes no keyword arguments" in message


@pytest.mark.parametrize(
    "source", ["list(1, 2)", "dict(1, 2, 3)", "str(b'ab', 'utf-8', 'x', 'y')"]
)
def test_no_refusal_names_a_dunder_or_a_call(source: str) -> None:
    message = _failure(source)
    assert "__init__" not in message
    assert "()" not in message
