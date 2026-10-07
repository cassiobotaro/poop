from functools import partial
from typing import Any

import pytest

from poop.transformers.range import RangeTransformer, _poop_range
from poop.types.boolean import true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.range import Range
from poop.types.string import Str
from tests._support import rewritten

_rewritten = partial(rewritten, RangeTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = range(5)", "x = _poop_range(5)"),
        ("x = myrange(5)", "x = myrange(5)"),
        ("f = range", "f = _poop_range_cls"),
    ],
    ids=["call", "other_names_untouched", "bare_name_to_mangled_binding"],
)
def test_range_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_bindings_contains_poop_range() -> None:
    assert "_poop_range" in RangeTransformer.BINDINGS


# --- _poop_range helper ---


def test_poop_range_stop_only() -> None:
    iv = _poop_range(Int(5))
    assert isinstance(iv, Range)
    assert list(iv._iter()) == [Int(0), Int(1), Int(2), Int(3), Int(4)]


def test_poop_range_start_stop() -> None:
    iv = _poop_range(Int(2), Int(5))
    assert list(iv._iter()) == [Int(2), Int(3), Int(4)]


def test_poop_range_start_stop_step() -> None:
    iv = _poop_range(Int(1), Int(10), Int(2))
    assert list(iv._iter()) == [Int(1), Int(3), Int(5), Int(7), Int(9)]


def test_poop_range_empty() -> None:
    iv = _poop_range(Int(0))
    assert list(iv._iter()) == []


def test_poop_range_negative_step() -> None:
    iv = _poop_range(Int(10), Int(0), Int(-1))
    assert list(iv._iter()) == [Int(i) for i in range(10, 0, -1)]


def test_poop_range_negative_step_with_stride() -> None:
    iv = _poop_range(Int(10), Int(0), Int(-2))
    assert list(iv._iter()) == [Int(i) for i in range(10, 0, -2)]


def test_poop_range_refuses_a_float_rather_than_truncating_it() -> None:
    # `int(3.5)` is 3, so the converter silently answered `range(0, 3)` for a
    # bound the program never wrote; `index` refuses, in CPython's words and
    # naming the wrapper by the builtin it stands for.
    bad: list[tuple[Any, ...]] = [
        (Float(3.5),),
        (Int(1), Float(9.0)),
        (Int(1), Int(9), Float(2.0)),
    ]
    for args in bad:
        with pytest.raises(TypeError) as info:
            _poop_range(*args)
        assert str(info.value) == "'float' object cannot be interpreted as an integer"


def test_poop_range_refuses_text_without_naming_int() -> None:
    # `int("3")` would have *succeeded*; the refusal a non-numeric argument got
    # was `int() argument must be a string, a bytes-like object or a real
    # number` — a call, for something the program spelt `range`.
    with pytest.raises(TypeError) as info:
        _poop_range(Str("3"))
    assert str(info.value) == "'str' object cannot be interpreted as an integer"


def test_poop_range_still_admits_the_boolean_rung() -> None:
    # Admitting `bool` is exactly what `index` is for: CPython's
    # `range(True, 5)` is `range(1, 5)`.
    admitted = _poop_range(true, Int(5))
    assert list(admitted._iter()) == [Int(i) for i in range(1, 5)]
