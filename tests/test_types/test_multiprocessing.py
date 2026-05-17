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
