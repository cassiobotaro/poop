"""The operator path's wording, and the pin that keeps it honest.

`poop_message` is the one place POOP reads another language's error text, so it
carries a risk none of the other rewordings do: CPython can change the sentence
under it. Python 3.14 already rewrote the unhashable-key error. The pins below
run the real operations and assert the shapes are still the ones the patterns
match — an upgrade that reworded them would leave the translation silently
falling through to Python's own text, and these fail instead.
"""

import pytest

from poop.types._message import article, binary_refusal, poop_message
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def test_arithmetic_shape_is_still_what_cpython_emits() -> None:
    # Pinned through POOP's own types, which is the only shape that matters:
    # raw `"a" + 1` answers `can only concatenate str (not "int") to str`,
    # str's own special case. A POOP Str is not a str, so both operands
    # answer NotImplemented and CPython falls back to the generic sentence.
    with pytest.raises(TypeError) as info:
        _ = Str("a") + Int(1)
    assert str(info.value) == "unsupported operand type(s) for +: 'str' and 'int'"


def test_comparison_shape_is_still_what_cpython_emits() -> None:
    with pytest.raises(TypeError) as info:
        _ = Int(1) < Str("a")
    assert str(info.value) == "'<' not supported between instances of 'int' and 'str'"


def test_arithmetic_failure_reads_as_a_refused_message() -> None:
    with pytest.raises(TypeError) as info:
        _ = Str("a") + Int(1)
    assert poop_message(info.value) == "str does not understand #+ with an int"


def test_comparison_failure_reads_as_a_refused_message() -> None:
    with pytest.raises(TypeError) as info:
        _ = Int(1) < Str("a")
    assert poop_message(info.value) == "int does not understand #< with a str"


def test_a_sort_surfaces_the_same_wording_from_inside_cpython() -> None:
    with pytest.raises(TypeError) as info:
        List(Int(1), Str("a")).sorted()
    assert poop_message(info.value) == "str does not understand #< with an int"


def test_pow_and_divmod_lose_the_builtin_call_from_the_selector() -> None:
    # CPython names these by the builtin that also reaches them; POOP has no
    # `pow()` or `divmod()` call, so the selector is the operator or message.
    with pytest.raises(TypeError) as info:
        _ = Int(2) ** Str("a")
    assert poop_message(info.value) == "int does not understand #** with a str"


def test_an_unmatched_message_passes_through_unchanged() -> None:
    # The degradation path: a shape POOP does not recognise must survive, not
    # crash or come back mangled.
    assert poop_message(ValueError("step must not be zero")) == "step must not be zero"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("int", "an int"),
        ("object", "an object"),
        ("str", "a str"),
        ("list", "a list"),
        ("", "a "),
    ],
)
def test_article_reads(name: str, expected: str) -> None:
    assert article(name) == expected


def test_binary_refusal_matches_message_not_understood_s_shape() -> None:
    # Deliberately the same register: `int does not understand #plus`. It is
    # the same kind of refusal, so it should read like one.
    assert binary_refusal("str", "+", "int") == "str does not understand #+ with an int"
