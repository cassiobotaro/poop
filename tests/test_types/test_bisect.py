from poop.interpreter import Interpreter
from poop.types.bisect import Bisect
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none

# --- bisect_left / bisect_right ---


def test_bisect_left_on_distinct() -> None:
    data = List(Int(1), Int(3), Int(5), Int(7))
    assert Bisect.bisect_left(data, Int(5))._value == 2


def test_bisect_right_on_distinct() -> None:
    data = List(Int(1), Int(3), Int(5), Int(7))
    assert Bisect.bisect_right(data, Int(5))._value == 3


def test_bisect_is_alias_of_bisect_right() -> None:
    data = List(Int(1), Int(3), Int(5), Int(7))
    assert Bisect.bisect(data, Int(5)) == Bisect.bisect_right(data, Int(5))


def test_bisect_left_with_duplicates() -> None:
    data = List(Int(1), Int(2), Int(2), Int(2), Int(3))
    assert Bisect.bisect_left(data, Int(2))._value == 1


def test_bisect_right_with_duplicates() -> None:
    data = List(Int(1), Int(2), Int(2), Int(2), Int(3))
    assert Bisect.bisect_right(data, Int(2))._value == 4


def test_bisect_left_with_lo_hi() -> None:
    data = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    assert Bisect.bisect_left(data, Int(3), Int(1), Int(4))._value == 2


def test_bisect_with_key() -> None:
    data = List(Int(1), Int(3), Int(5))
    assert Bisect.bisect_left(data, 10, key=lambda x: x._value * 2)._value == 2


# --- insort_* ---


def test_insort_left_inserts_in_order() -> None:
    data = List(Int(1), Int(3), Int(5))
    result = Bisect.insort_left(data, Int(2))
    assert result is none
    assert data == List(Int(1), Int(2), Int(3), Int(5))


def test_insort_right_inserts_after_equal() -> None:
    data = List(Int(1), Int(2), Int(3))
    Bisect.insort_right(data, Int(2))
    # Inserted after existing 2 → [1, 2, 2, 3]
    assert data == List(Int(1), Int(2), Int(2), Int(3))


def test_insort_is_alias_of_insort_right() -> None:
    a = List(Int(1), Int(3))
    b = List(Int(1), Int(3))
    Bisect.insort(a, Int(2))
    Bisect.insort_right(b, Int(2))
    assert a == b


def test_insort_with_lo_hi() -> None:
    data = List(Int(1), Int(3), Int(5))
    Bisect.insort_left(data, Int(4), Int(1), Int(3))
    assert data == List(Int(1), Int(3), Int(4), Int(5))


# --- Interpreter ---


def test_bisect_reachable_via_interpreter() -> None:
    Interpreter().run_source("bisect.bisect([1, 3, 5], 4).print()")


def test_insort_reachable_via_interpreter() -> None:
    Interpreter().run_source("xs = [1, 3, 5]\nbisect.insort(xs, 2)\nxs.print()")
