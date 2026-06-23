"""Tests for the multiprocessing namespace.

Most tests exercise only construction and the namespace shape. Tests
that actually fork worker processes are flagged as slow / off-by-default
because Python 3.14 changed the default start method to ``forkserver``
on Linux, which makes the worker spin up a fresh interpreter — even
trivial tests pay a multi-second startup cost and the forkserver state
interacts badly with the pytest collector.
"""

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.multiprocessing import MPQueue, Multiprocessing, Pool, Process
from poop.types.none import none
from poop.types.string import Str

# --- Process construction & shape ---


def test_process_constructs_default() -> None:
    p = Process()
    assert isinstance(p, Process)


def test_process_constructs_with_target() -> None:
    p = Process(target=lambda: None)
    assert isinstance(p, Process)


def test_process_constructs_with_name_and_daemon() -> None:
    p = Process(target=lambda: None, name=Str("w"), daemon=true)
    assert p.name == Str("w")


def test_process_pid_initially_none() -> None:
    p = Process(target=lambda: None)
    # Before start, pid is None.
    assert p.pid is none


def test_process_exitcode_initially_none() -> None:
    p = Process(target=lambda: None)
    assert p.exitcode is none


def test_process_is_alive_returns_boolean() -> None:
    p = Process(target=lambda: None)
    assert isinstance(p.is_alive(), Boolean)


def test_process_name_property() -> None:
    p = Process(name=Str("foo"))
    assert p.name == Str("foo")


# --- MPQueue construction & shape ---
#
# `multiprocessing.Queue` works without actually forking, so these are
# fully exercised.


def test_mpqueue_constructs_default() -> None:
    q = MPQueue()
    try:
        assert isinstance(q, MPQueue)
    finally:
        q.close()


def test_mpqueue_constructs_with_maxsize() -> None:
    q = MPQueue(Int(5))
    try:
        assert isinstance(q, MPQueue)
    finally:
        q.close()


def test_mpqueue_put_get_roundtrips_poop_value() -> None:
    # proposal 134: a POOP value must survive put/get (it crashed the
    # feeder's pickling and deadlocked get() before).
    q = MPQueue()
    try:
        q.put(Int(1))
        assert q.get(timeout=Float(5.0)) == Int(1)
        q.put(Str("hello"))
        assert q.get(timeout=Float(5.0)) == Str("hello")
        q.put(List(Int(1), Int(2)))
        assert q.get(timeout=Float(5.0)) == List(Int(1), Int(2))
    finally:
        q.close()


def test_mpqueue_empty_returns_boolean() -> None:
    q = MPQueue()
    try:
        assert isinstance(q.empty(), Boolean)
    finally:
        q.close()


def test_mpqueue_full_returns_boolean() -> None:
    q = MPQueue()
    try:
        assert isinstance(q.full(), Boolean)
    finally:
        q.close()


def test_mpqueue_close_returns_none() -> None:
    q = MPQueue()
    assert q.close() is none


# --- Pool construction ---


def test_pool_close_join_returns_none() -> None:
    pool = Pool(Int(2))
    assert pool.close() is none
    assert pool.join() is none


def test_pool_terminate_join_returns_none() -> None:
    pool = Pool(Int(2))
    assert pool.terminate() is none
    pool.join()


# --- Module helpers ---


def test_cpu_count_returns_int() -> None:
    assert isinstance(Multiprocessing.cpu_count(), Int)


def test_active_children_returns_list() -> None:
    assert isinstance(Multiprocessing.active_children(), List)


def test_current_process_returns_process() -> None:
    assert isinstance(Multiprocessing.current_process(), Process)


def test_get_start_method_returns_str_or_none() -> None:
    result = Multiprocessing.get_start_method()
    assert isinstance(result, Str) or result is none


def test_get_start_method_allow_none_true() -> None:
    result = Multiprocessing.get_start_method(true)
    assert isinstance(result, Str) or result is none


def test_multiprocessing_class_refs() -> None:
    assert Multiprocessing.Process is Process
    assert Multiprocessing.Queue is MPQueue
    assert Multiprocessing.Pool is Pool


# --- Interpreter integration ---


def test_multiprocessing_via_interpreter() -> None:
    Interpreter().run_source("multiprocessing.cpu_count().print()")


def test_pool_context_manager() -> None:
    with Pool(Int(1)) as pool:
        assert isinstance(pool, Pool)


def test_process_close_returns_none_after_construction() -> None:
    # close() on a never-started Process is a no-op that returns POOP `none`.
    p = Process(target=lambda: None)
    assert p.close() is none


# --- Pool result wrapping (raw-object leak fixes) ---


class _StubPoolImpl:
    """Stand-in for `multiprocessing.pool.Pool` that returns raw Python
    values, mimicking what comes back across the (pickled) process boundary —
    without paying the forkserver cost of a real Pool."""

    def apply(self, func: object, args: object = None) -> object:
        return 25

    def map(self, func: object, iterable: object) -> list[int]:
        return [1, 4, 9]


def test_pool_apply_wraps_raw_worker_result() -> None:
    # Proposal 200: the worker result returns as a raw Python object; apply
    # must re-wrap it so it stays a POOP value.
    pool = Pool.__new__(Pool)
    pool._impl = _StubPoolImpl()
    result = pool.apply(lambda: None)
    assert isinstance(result, Int)
    assert result == Int(25)


def test_pool_map_wraps_each_raw_element() -> None:
    # Proposal 201: each element returns raw; map must wrap every element,
    # not just the outer List.
    pool = Pool.__new__(Pool)
    pool._impl = _StubPoolImpl()
    result = pool.map(lambda x: x, List(Int(1), Int(2), Int(3)))
    assert isinstance(result, List)
    assert all(isinstance(e, Int) for e in result)
    assert result == List(Int(1), Int(4), Int(9))
