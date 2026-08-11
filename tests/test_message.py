"""The operator path's wording, and the pin that keeps it honest.

`poop_message` is the one place POOP reads another language's error text, so it
carries a risk none of the other rewordings do: CPython can change the sentence
under it. Python 3.14 already rewrote the unhashable-key error. The pins below
run the real operations and assert the shapes are still the ones the patterns
match — an upgrade that reworded them would leave the translation silently
falling through to Python's own text, and these fail instead.
"""

import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.types._message import article, binary_refusal, poop_message
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
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


# Proposal 55. `no_hash` bans `hash(x)` and names `obj.hash()`; the substitute
# answered CPython's bare `unhashable type: 'list'` on nine receivers, while the
# two places that reach the same condition — a set element and a dict key —
# answered a sentence that says where the value was going.
@pytest.mark.parametrize(
    "source",
    [
        "[1, 2].hash()",
        '{"a": 1}.hash()',
        "{1, 2}.hash()",
        'bytearray(b"ab").hash()',
        '{"a": 1}.keys().hash()',
        '{"a": 1}.values().hash()',
        '{"a": 1}.items().hash()',
        "([1, 2],).hash()",
    ],
)
def test_hash_says_why_and_where(source: str) -> None:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    message = str(info.value)
    assert "cannot be hashed" in message
    assert "a set element or a dict key" in message
    # CPython's own text is kept in parentheses, as the storage sites keep it.
    assert "unhashable type:" in message


def test_hash_and_the_storage_sites_name_the_same_class() -> None:
    # The disagreement the item was: one condition, three call sites, and only
    # `hash` spoke CPython.
    def failure(source: str) -> str:
        with pytest.raises(PoopError) as info:
            Interpreter().run_source(source + "\n")
        return str(info.value)

    assert "'list'" in failure("[1].hash()")
    assert "'list'" in failure("{[1]}")
    assert "'list'" in failure("{}.at_put([1], 2)")


def test_a_writable_memoryview_gets_its_own_reason() -> None:
    # A `ValueError`, not the `TypeError` the rewrite matches, and the only
    # sentence in the language that said *object* where POOP says receiver.
    with pytest.raises(PoopError) as info:
        Interpreter().run_source('memoryview(bytearray(b"ab")).hash()\n')
    message = str(info.value)
    assert "a memoryview over a bytearray cannot be hashed" in message
    assert "writable" not in message
    assert "object" not in message


def test_a_hashable_receiver_still_answers_its_hash() -> None:
    Interpreter().run_source('("abc".hash() == "abc".hash()).assert_()\n')
    Interpreter().run_source('memoryview(b"ab").hash()\n')


def test_an_unmatched_type_error_passes_through() -> None:
    # The rule `_message`'s docstring sets for every rewrite in it: anything
    # unrecognised degrades to the old behaviour rather than to a crash.
    from poop.types._message import cannot_be_hashed

    assert cannot_be_hashed(TypeError("something else entirely")) is None
    assert cannot_be_hashed(TypeError("unhashable type: 'list'")) is not None


def test_a_type_error_that_is_not_about_hashing_is_re_raised() -> None:
    # The pass-through branch. No wrapper produces one, so it is built here:
    # the point of the rule is that an upstream rewording degrades to CPython's
    # sentence rather than to a wrong POOP one.
    class Odd(Object):
        __slots__ = ()

        def __hash__(self) -> int:
            raise TypeError("something else entirely")

    with pytest.raises(TypeError, match="something else entirely"):
        Odd().hash()
