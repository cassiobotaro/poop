"""Two sentinels, one test module, since the two modules share a name.

`poop/types/_sentinel.py` holds POOP's internal markers (`MISSING` for an
argument not given); `poop/types/sentinel.py` is Python 3.15's `sentinel`
builtin, held to CPython's answers — checked against `python3.15` first:
`sentinel("M") is sentinel("M")` is False there, `==` and `hash` follow
identity, `bool` is True, and `repr` is the name or the `repr` keyword.
"""

import pytest

from poop import Interpreter
from poop.errors import ExecutionError
from poop.types._sentinel import MISSING, NOT_A_COUNT
from poop.types._sentinel import Sentinel as _Marker
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.sentinel import Sentinel
from poop.types.string import Str

# the internal markers


def test_a_marker_names_itself_rather_than_an_address() -> None:
    assert repr(MISSING) == "<missing>"
    assert repr(NOT_A_COUNT) == "<not_a_count>"


def test_every_marker_is_distinct() -> None:
    # One enum, but distinct members: "argument not given" must never be read
    # as "not a repeat count" or "nothing buffered".
    assert len(set(_Marker)) == len(_Marker.__members__)


# the builtin


def test_prints_as_its_name() -> None:
    assert str(Sentinel(Str("MISSING"))) == "MISSING"
    assert repr(Sentinel(Str("MISSING"))) == "MISSING"
    assert Sentinel(Str("")).print  # an empty name is CPython's too


def test_the_repr_keyword_wins_over_the_name() -> None:
    assert repr(Sentinel(Str("X"), Str("<X>"))) == "<X>"


def test_class_name_answers_sentinel() -> None:
    assert Sentinel(Str("X")).class_name() == Str("sentinel")


def test_every_call_is_a_new_object() -> None:
    # `sentinel("M") is sentinel("M")` is False in CPython 3.15, and so are
    # `==` and an equal hash: identity is the one thing a sentinel has.
    a, b = Sentinel(Str("M")), Sentinel(Str("M"))
    assert a.is_identical(b) is false
    assert (a == b) is false
    assert a.is_identical(a) is true
    assert (a == a) is true
    assert a.hash() == a.hash()


def test_truthy_and_hashable() -> None:
    marker = Sentinel(Str("M"))
    assert bool(marker) is True
    d = Dict()
    d.at_put(marker, Int(1))
    assert d.at(marker) == Int(1)


def test_declines_the_union_operator() -> None:
    # `int | MISSING` builds a typing union in CPython, for annotations POOP
    # does not write; here it is an operand like any other.
    with pytest.raises(
        ExecutionError, match="int does not understand #\\| with a sentinel"
    ):
        Interpreter().run_source('5 | sentinel("M")')
    with pytest.raises(
        ExecutionError, match="sentinel does not understand #\\| with an int"
    ):
        Interpreter().run_source('sentinel("M") | 5')


def test_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    Interpreter().run_source(
        'MISSING = sentinel("MISSING")\n'
        "MISSING.print()\n"
        'sentinel("X", repr="<X>").print()\n'
        "MISSING.is_identical(MISSING).print()\n"
        'MISSING.is_identical(sentinel("MISSING")).print()\n'
        "MISSING.class_name().print()\n"
        "MISSING.is_instance(sentinel).print()\n"
        "class Marker(sentinel):\n"
        "    pass\n"
        'Marker("K").print()\n'
        'Marker("K").class_name().print()\n'
    )
    assert capsys.readouterr().out == (
        "MISSING\n<X>\nTrue\nFalse\nsentinel\nTrue\nK\nMarker\n"
    )
