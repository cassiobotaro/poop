import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.heapq import HeapMerge, Heapq
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none


def test_heappush_returns_none() -> None:
    heap = List()
    result = Heapq.heappush(heap, Int(3))
    assert result is none
    assert heap == List(Int(3))


def test_heappush_maintains_heap_property() -> None:
    heap = List()
    Heapq.heappush(heap, Int(5))
    Heapq.heappush(heap, Int(1))
    Heapq.heappush(heap, Int(3))
    # Smallest is always at the root.
    assert heap.at(Int(0)) == Int(1)


def test_heappop_returns_smallest() -> None:
    heap = List(Int(1), Int(3), Int(5))
    smallest = Heapq.heappop(heap)
    assert smallest == Int(1)
    assert heap == List(Int(3), Int(5))


def test_heappop_empty_raises_index_error() -> None:
    with pytest.raises(IndexError):
        Heapq.heappop(List())


def test_heappushpop_in_one_step() -> None:
    heap = List(Int(2), Int(4), Int(6))
    result = Heapq.heappushpop(heap, Int(1))
    # Pushed 1 is smaller than 2, so 1 pops out, heap unchanged.
    assert result == Int(1)
    assert heap == List(Int(2), Int(4), Int(6))


def test_heapreplace_pops_then_pushes() -> None:
    heap = List(Int(2), Int(4), Int(6))
    result = Heapq.heapreplace(heap, Int(5))
    # Pops 2 first, then pushes 5.
    assert result == Int(2)
    assert Int(5) in [heap.at(Int(i)) for i in range(3)]


def test_heapify_in_place() -> None:
    data = List(Int(5), Int(1), Int(3), Int(2), Int(4))
    result = Heapq.heapify(data)
    assert result is none
    assert data.at(Int(0)) == Int(1)  # smallest now at root


def test_nlargest_returns_list() -> None:
    data = List(Int(3), Int(1), Int(4), Int(1), Int(5), Int(9))
    result = Heapq.nlargest(Int(3), data)
    assert isinstance(result, List)
    assert result == List(Int(9), Int(5), Int(4))


def test_nsmallest_returns_list() -> None:
    data = List(Int(3), Int(1), Int(4), Int(1), Int(5), Int(9))
    result = Heapq.nsmallest(Int(3), data)
    assert isinstance(result, List)
    assert result == List(Int(1), Int(1), Int(3))


def test_nlargest_with_key() -> None:
    data = List(Int(-3), Int(-1), Int(-5))
    # Largest by absolute value.
    result = Heapq.nlargest(Int(2), data, key=lambda x: abs(x._value))
    assert isinstance(result, List)
    assert result.len()._value == 2


def test_merge_returns_heap_merge() -> None:
    result = Heapq.merge(
        [Int(1), Int(4), Int(7)],
        [Int(2), Int(5), Int(8)],
    )
    assert isinstance(result, HeapMerge)


def test_merge_iterates_sorted() -> None:
    merged = Heapq.merge(
        [Int(1), Int(4), Int(7)],
        [Int(2), Int(5), Int(8)],
    )
    result = merged.to_list()
    assert result == List(Int(1), Int(2), Int(4), Int(5), Int(7), Int(8))


def test_merge_reverse() -> None:
    merged = Heapq.merge(
        [Int(7), Int(4), Int(1)],
        [Int(8), Int(5), Int(2)],
        reverse=true,
    )
    result = merged.to_list()
    assert result == List(Int(8), Int(7), Int(5), Int(4), Int(2), Int(1))


def test_merge_iter_does_not_leak_raw_generator() -> None:
    # __iter__ must not hand back the raw stdlib `heapq.merge` generator —
    # iterating a POOP iterator should go through a generator the wrapper
    # owns, never exposing a non-POOP builtins.generator object.
    merged = Heapq.merge([Int(1), Int(4)], [Int(2)])
    iterator = iter(merged)
    assert iterator is not merged._gen


def test_merge_iter_yields_wrapped_elements() -> None:
    merged = Heapq.merge([Int(1), Int(4)], [Int(2)])
    elements = list(iter(merged))
    assert all(isinstance(e, Int) for e in elements)
    assert elements == [Int(1), Int(2), Int(4)]


def test_heapq_reachable_via_interpreter() -> None:
    Interpreter().run_source("heapq.nlargest(2, [3, 1, 4]).len().print()")
