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
        # Four, not three: the text form takes `(text, encoding, errors)` on
        # both, as CPython's does.
        (
            "bytearray('ab', 'utf-8', 'strict', 1)",
            "bytearray is built from at most one",
        ),
        ("bytes('a', 'utf-8', 'strict', 1)", "bytes is built from at most one source"),
        # Proposal 44: eight of the eighteen still answered CPython's call
        # machinery, each naming the builtin spelt as a *call* and saying
        # "positional argument" — which the wording sweep bans outright.
        ("float(5, 5)", "float is built from at most one number or string"),
        ("bool(5, 5)", "bool is built from at most one value to test"),
        ("int(1, 2, 3)", "int is built from at most a value and a base"),
        ("range(1, 2, 3, 4)", "range is built from a stop"),
        ("enumerate([1], 1, 2)", "enumerate is built from a collection"),
        ("object(5)", "object is built from nothing"),
        # The sharpest of the eight: `slice.__init__() takes from 1 to 4
        # positional arguments`, naming a dunder from a construct the program
        # spelled without one. `Slice(...)` *is* the call (proposal 9), so this
        # was the one constructor with no factory at all.
        ("slice(1, 2, 3, 4)", "slice is built from a stop"),
    ],
)
def test_an_over_supplied_constructor_is_refused(source: str, expected: str) -> None:
    assert expected in _failure(source)


@pytest.mark.parametrize(
    "builtin",
    [
        "list",
        "tuple",
        "set",
        "frozenset",
        "memoryview",
        "bytearray",
        "bytes",
        # The keyword half leaked on all eight too.
        "float",
        "bool",
        "int",
        "range",
        "enumerate",
        "object",
        "slice",
    ],
)
def test_a_keyword_is_refused_by_the_converter(builtin: str) -> None:
    message = _failure(f"{builtin}(x=1)")
    assert f"{builtin} takes no keyword arguments" in message


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("range()", "range is built from a stop"),
        ("enumerate()", "enumerate is built from a collection"),
        ("slice()", "slice is built from a stop"),
    ],
)
def test_an_under_supplied_constructor_is_refused(source: str, expected: str) -> None:
    # The other half of the guard: these three need at least one argument, and
    # CPython's `missing 1 required positional argument: 'stop_or_start'` named
    # both the calling convention and the converter's own parameter name.
    message = _failure(source)
    assert expected in message
    assert "got nothing" in message
    assert "positional argument" not in message


def test_object_is_the_one_constructor_built_from_nothing() -> None:
    Interpreter().run_source("object().print()\n")
    Interpreter().run_source("Object().print()\n")


def test_zip_refuses_only_the_keyword_it_does_not_have() -> None:
    # `zip` legitimately takes any number of positional arguments, so there is
    # no arity to guard — only `strict` is a real keyword.
    assert "zip takes no keyword argument 'nope'" in _failure("zip([1], nope=1)")


# The sweep the proposal describes: every bare constructor name, called with
# five arguments and with an unknown keyword, must answer a sentence carrying
# none of the wording sweep's banned patterns. That enumeration is what counted
# the eight, and it is what stops a ninth from shipping unguarded.
_CONSTRUCTORS = [
    "list",
    "tuple",
    "set",
    "frozenset",
    "dict",
    "str",
    "bytes",
    "bytearray",
    "memoryview",
    "int",
    "float",
    "bool",
    "complex",
    "range",
    "enumerate",
    "zip",
    "object",
    "slice",
]


@pytest.mark.parametrize("builtin", _CONSTRUCTORS)
def test_no_constructor_answers_cpython_call_machinery(builtin: str) -> None:
    from poop.errors import PoopError
    from tests.test_no_python_wording import _FORBIDDEN

    for source in (f"{builtin}(1, 2, 3, 4, 5)", f"{builtin}(nope=1)"):
        try:
            Interpreter().run_source(source)
        except PoopError as exc:
            message = str(exc)
        else:
            # `dict(a=1)` is the one constructor that legitimately takes a
            # keyword, so there is nothing to word.
            continue
        named = [
            construct
            for construct, pattern in _FORBIDDEN.items()
            if pattern.search(message)
        ]
        assert named == [], f"{source!r} answered {message!r}, naming {named}"


@pytest.mark.parametrize(
    "source", ["list(1, 2)", "dict(1, 2, 3)", "str(b'ab', 'utf-8', 'x', 'y')"]
)
def test_no_refusal_names_a_dunder_or_a_call(source: str) -> None:
    message = _failure(source)
    assert "__init__" not in message
    assert "()" not in message
