import pytest

from poop.types.int import Int
from poop.types.list import List
from poop.types.map import Map


def test_map_is_lazy() -> None:
    """Block must not run until Map is consumed."""
    calls: list[int] = []

    def block(x: Int) -> Int:
        calls.append(x._value)
        return Int(x._value * 10)

    m = Map(List(Int(1), Int(2), Int(3)), block)
    assert calls == []
    list(m)
    assert calls == [1, 2, 3]


def test_map_next_advances_one_at_a_time() -> None:
    m = Map(List(Int(1), Int(2), Int(3)), lambda x: Int(x._value * 10))
    assert m.next() == Int(10)
    assert m.next() == Int(20)
    assert m.next() == Int(30)


def test_map_next_raises_stop_iteration_when_exhausted() -> None:
    m = Map(List(Int(1)), lambda x: x)
    m.next()
    with pytest.raises(StopIteration):
        m.next()


def test_map_is_one_shot() -> None:
    # Matches Python's map: once exhausted, further iteration is empty.
    src = List(Int(1), Int(2))
    m = Map(src, lambda x: Int(x._value + 100))
    first = list(m)
    second = list(m)
    assert first == [Int(101), Int(102)]
    assert second == []


def test_map_self_iter_returns_self() -> None:
    m = Map(List(Int(1)), lambda x: x)
    assert m.iter() is m


def test_map_chains_lazily() -> None:
    src = List(Int(1), Int(2), Int(3))
    chain = Map(Map(src, lambda x: Int(x._value + 1)), lambda x: Int(x._value * 10))
    assert list(chain) == [Int(20), Int(30), Int(40)]


def test_map_materializes_via_list_constructor() -> None:
    m = Map(List(Int(1), Int(2)), lambda x: Int(x._value + 5))
    assert List(*m) == List(Int(6), Int(7))


def test_map_str_repr() -> None:
    m = Map(List(), lambda x: x)
    assert str(m) == "<map>"
    assert repr(m) == "<map>"


def test_map_eq_is_identity() -> None:
    src = List(Int(1))
    a = Map(src, lambda x: x)
    b = Map(src, lambda x: x)
    assert a == a
    assert not (a == b)
