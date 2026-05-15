import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.graphlib import Graphlib, TopologicalSorter
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_static_order_returns_topo_sorted_tuple() -> None:
    # b depends on a; c depends on b. Order: a, b, c.
    graph = Dict().at_put(Str("b"), List(Str("a"))).at_put(Str("c"), List(Str("b")))
    sorter = TopologicalSorter(graph)
    order = sorter.static_order()
    assert isinstance(order, Tuple)
    seq = [order.at(Int(i)) for i in range(order.len()._value)]
    assert seq.index(Str("a")) < seq.index(Str("b")) < seq.index(Str("c"))


def test_empty_constructor() -> None:
    sorter = TopologicalSorter()
    assert isinstance(sorter.static_order(), Tuple)


def test_add_incrementally() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("b"), Str("a"))
    sorter.add(Str("c"), Str("b"))
    order = sorter.static_order()
    seq = [order.at(Int(i)) for i in range(order.len()._value)]
    assert seq.index(Str("a")) < seq.index(Str("c"))


def test_add_returns_none() -> None:
    sorter = TopologicalSorter()
    result = sorter.add(Str("a"))
    assert result is none


def test_prepare_returns_none() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("a"))
    result = sorter.prepare()
    assert result is none


def test_is_active_before_prepare() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("a"))
    sorter.prepare()
    assert sorter.is_active() is true


def test_get_ready_returns_tuple() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("a"))
    sorter.prepare()
    ready = sorter.get_ready()
    assert isinstance(ready, Tuple)
    # "a" has no predecessors → ready immediately.
    assert Str("a") in [ready.at(Int(i)) for i in range(ready.len()._value)]


def test_done_returns_none_and_advances() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("b"), Str("a"))
    sorter.prepare()
    initial = sorter.get_ready()
    items = [initial.at(Int(i)) for i in range(initial.len()._value)]
    assert Str("a") in items
    result = sorter.done(Str("a"))
    assert result is none
    next_ready = sorter.get_ready()
    next_items = [next_ready.at(Int(i)) for i in range(next_ready.len()._value)]
    assert Str("b") in next_items


def test_cycle_raises_error() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("a"), Str("b"))
    sorter.add(Str("b"), Str("a"))
    with pytest.raises(Graphlib.CycleError):
        sorter.static_order()


def test_is_active_after_full_consumption() -> None:
    sorter = TopologicalSorter()
    sorter.add(Str("a"))
    sorter.prepare()
    sorter.get_ready()
    sorter.done(Str("a"))
    assert sorter.is_active() is false


def test_graphlib_reachable_via_interpreter() -> None:
    Interpreter().run_source("TopologicalSorter().static_order().len().print()")


def test_TopologicalSorter_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["TopologicalSorter"] is TopologicalSorter
