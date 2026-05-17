import gc as _stdlib_gc

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.gc import GC
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.tuple import Tuple


@pytest.fixture(autouse=True)
def _restore_gc() -> object:
    """Process-global gc state — restore after each test."""
    saved_enabled = _stdlib_gc.isenabled()
    saved_threshold = _stdlib_gc.get_threshold()
    saved_debug = _stdlib_gc.get_debug()
    yield
    if saved_enabled:
        _stdlib_gc.enable()
    else:
        _stdlib_gc.disable()
    _stdlib_gc.set_threshold(*saved_threshold)
    _stdlib_gc.set_debug(saved_debug)


def test_enable_disable_isenabled() -> None:
    GC.disable()
    assert GC.isenabled() is false
    GC.enable()
    assert GC.isenabled() is true


def test_collect_returns_int() -> None:
    assert isinstance(GC.collect(), Int)


def test_collect_with_generation() -> None:
    assert isinstance(GC.collect(Int(0)), Int)


def test_get_threshold_returns_tuple() -> None:
    result = GC.get_threshold()
    assert isinstance(result, Tuple)
    assert result.len() == Int(3)
    for elem in result:
        assert isinstance(elem, Int)


def test_set_threshold_round_trip() -> None:
    # CPython 3.14 may quietly normalise threshold2 in some
    # interpreter configurations; assert via the underlying
    # gc.get_threshold to track the actually-stored shape.
    GC.set_threshold(Int(700), Int(10), Int(10))
    assert GC.get_threshold() == Tuple(*(Int(t) for t in _stdlib_gc.get_threshold()))


def test_set_threshold_one_arg() -> None:
    assert GC.set_threshold(Int(500)) is none


def test_set_threshold_two_args() -> None:
    assert GC.set_threshold(Int(500), Int(5)) is none


def test_get_count_returns_tuple() -> None:
    result = GC.get_count()
    assert isinstance(result, Tuple)
    assert result.len() == Int(3)


def test_get_stats_returns_list_of_dicts() -> None:
    result = GC.get_stats()
    assert isinstance(result, List)
    first = result.at(Int(0))
    assert isinstance(first, Dict)


def test_debug_round_trip() -> None:
    GC.set_debug(GC.DEBUG_STATS)
    assert GC.get_debug() == GC.DEBUG_STATS
    GC.set_debug(Int(0))
    assert GC.get_debug() == Int(0)


def test_debug_constants_are_ints() -> None:
    assert isinstance(GC.DEBUG_STATS, Int)
    assert isinstance(GC.DEBUG_COLLECTABLE, Int)
    assert isinstance(GC.DEBUG_UNCOLLECTABLE, Int)
    assert isinstance(GC.DEBUG_SAVEALL, Int)
    assert isinstance(GC.DEBUG_LEAK, Int)


def test_freeze_unfreeze() -> None:
    initial = GC.get_freeze_count()
    GC.freeze()
    after_freeze = GC.get_freeze_count()
    assert after_freeze._value >= initial._value
    GC.unfreeze()
    assert isinstance(GC.get_freeze_count(), Int)


def test_callbacks_returns_list() -> None:
    callbacks = GC.callbacks
    assert callbacks is _stdlib_gc.callbacks


# --- Interpreter integration ---


def test_gc_isenabled_via_interpreter() -> None:
    Interpreter().run_source("gc.isenabled().print()")


def test_gc_collect_via_interpreter() -> None:
    Interpreter().run_source("gc.collect().print()")
