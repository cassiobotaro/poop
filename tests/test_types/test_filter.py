import pytest

from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers.filter import FilterTransformer
from poop.types.filter import Filter
from poop.types.int import Int
from poop.types.list import List


def test_filter_is_lazy() -> None:
    calls: list[int] = []

    def keep_even(x: Int) -> bool:
        calls.append(x._value)
        return x._value % 2 == 0

    f = Filter(List(Int(1), Int(2), Int(3)), keep_even)
    assert calls == []
    list(f)
    assert calls == [1, 2, 3]


def test_filter_keeps_truthy_results() -> None:
    f = Filter(List(Int(1), Int(2), Int(3), Int(4)), lambda x: x._value % 2 == 0)
    assert list(f) == [Int(2), Int(4)]


def test_filter_next_advances_one_at_a_time() -> None:
    f = Filter(List(Int(1), Int(2), Int(3), Int(4)), lambda x: x._value > 2)
    assert f.next() == Int(3)
    assert f.next() == Int(4)


def test_filter_next_raises_stop_iteration_when_exhausted() -> None:
    f = Filter(List(Int(1), Int(2)), lambda x: x._value > 100)
    with pytest.raises(StopIteration):
        f.next()


def test_filter_iter_creates_fresh_generator_when_source_is_restartable() -> None:
    src = List(Int(1), Int(2), Int(3))
    f = Filter(src, lambda x: x._value > 1)
    first = list(f)
    second = list(f)
    assert first == [Int(2), Int(3)]
    assert second == [Int(2), Int(3)]


def test_filter_self_iter_returns_self() -> None:
    f = Filter(List(Int(1)), lambda x: True)
    assert f.iter() is f


def test_filter_chains_lazily() -> None:
    src = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    chain = Filter(
        Filter(src, lambda x: x._value > 1),
        lambda x: x._value % 2 == 0,
    )
    assert list(chain) == [Int(2), Int(4)]


def test_filter_materializes_via_list_constructor() -> None:
    f = Filter(List(Int(1), Int(2), Int(3)), lambda x: x._value >= 2)
    assert List(*f) == List(Int(2), Int(3))


def test_filter_is_in_default_namespace() -> None:
    assert DEFAULT_NAMESPACE["Filter"] is Filter


def test_filter_binding_in_transformer() -> None:
    assert FilterTransformer.BINDINGS["Filter"] is Filter


def test_filter_str_repr() -> None:
    f = Filter(List(), lambda x: True)
    assert str(f) == "<filter>"
    assert repr(f) == "<filter>"


def test_filter_eq_is_identity() -> None:
    src = List(Int(1))
    a = Filter(src, lambda x: True)
    b = Filter(src, lambda x: True)
    assert a == a
    assert not (a == b)
