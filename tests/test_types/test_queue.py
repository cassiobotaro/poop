import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import none
from poop.types.queue import (
    LifoQueue,
    PriorityQueue,
    Queue,
    QueueNamespace,
    SimpleQueue,
)

# --- Queue (FIFO) ---


def test_queue_constructs_default() -> None:
    assert isinstance(Queue(), Queue)


def test_queue_constructs_with_maxsize() -> None:
    assert isinstance(Queue(Int(5)), Queue)


def test_queue_treats_poop_none_maxsize_as_unbounded() -> None:
    # POOP `none` for the optional maxsize must behave like a missing arg.
    q = Queue(none)
    assert q.full() is false
    assert isinstance(LifoQueue(none), LifoQueue)
    assert isinstance(PriorityQueue(none), PriorityQueue)


def test_queue_put_get_round_trip() -> None:
    q = Queue()
    assert q.put(Int(1)) is none
    assert q.get() == Int(1)


def test_queue_put_with_block_and_timeout() -> None:
    from poop.types.float import Float

    q = Queue()
    assert q.put(Int(1), true, Float(1.0)) is none


def test_queue_put_nowait_and_get_nowait() -> None:
    q = Queue()
    assert q.put_nowait(Int(2)) is none
    assert q.get_nowait() == Int(2)


def test_queue_size_empty_full() -> None:
    q = Queue(Int(2))
    assert q.empty() is true
    q.put(Int(1))
    q.put(Int(2))
    assert q.qsize() == Int(2)
    assert q.full() is true


def test_queue_task_done_and_join() -> None:
    q = Queue()
    q.put(Int(1))
    q.get()
    assert q.task_done() is none
    assert q.join() is none


def test_queue_get_with_block_and_timeout() -> None:
    from poop.types.float import Float

    q = Queue()
    q.put(Int(7))
    assert q.get(true, Float(1.0)) == Int(7)


# --- LifoQueue ---


def test_lifo_constructs() -> None:
    assert isinstance(LifoQueue(), LifoQueue)
    assert isinstance(LifoQueue(Int(5)), LifoQueue)


def test_lifo_order() -> None:
    q = LifoQueue()
    q.put(Int(1))
    q.put(Int(2))
    assert q.get() == Int(2)
    assert q.get() == Int(1)


def test_lifo_task_done_and_join() -> None:
    q = LifoQueue()
    q.put(Int(1))
    q.get()
    assert q.task_done() is none
    assert q.join() is none


# --- PriorityQueue ---


def test_priority_constructs() -> None:
    assert isinstance(PriorityQueue(), PriorityQueue)
    assert isinstance(PriorityQueue(Int(5)), PriorityQueue)


def test_priority_order() -> None:
    q = PriorityQueue()
    # Use Python ints to ensure heap ordering works (POOP Ints compare).
    q.put(Int(3))
    q.put(Int(1))
    q.put(Int(2))
    assert q.get() == Int(1)


def test_priority_task_done_and_join() -> None:
    q = PriorityQueue()
    q.put(Int(1))
    q.get()
    assert q.task_done() is none
    assert q.join() is none


# --- SimpleQueue ---


def test_simple_constructs() -> None:
    assert isinstance(SimpleQueue(), SimpleQueue)


def test_simple_put_get() -> None:
    q = SimpleQueue()
    assert q.put(Int(1)) is none
    assert q.get() == Int(1)


def test_simple_put_nowait_get_nowait() -> None:
    q = SimpleQueue()
    q.put_nowait(Int(2))
    assert q.get_nowait() == Int(2)


def test_simple_get_with_args() -> None:
    from poop.types.float import Float

    q = SimpleQueue()
    q.put(Int(3))
    assert q.get(true, Float(1.0)) == Int(3)


def test_simple_qsize_and_empty() -> None:
    q = SimpleQueue()
    assert q.empty() is true
    q.put(Int(1))
    assert q.qsize() == Int(1)


# --- Errors ---


def test_queue_empty_raises_empty_class() -> None:
    q = Queue()
    with pytest.raises(QueueNamespace.Empty):
        q.get_nowait()


def test_queue_full_raises_full_class() -> None:
    q = Queue(Int(1))
    q.put_nowait(Int(1))
    with pytest.raises(QueueNamespace.Full):
        q.put_nowait(Int(2))


def test_queue_class_refs() -> None:
    assert QueueNamespace.Queue is Queue
    assert QueueNamespace.LifoQueue is LifoQueue
    assert QueueNamespace.PriorityQueue is PriorityQueue
    assert QueueNamespace.SimpleQueue is SimpleQueue


# --- Interpreter integration ---


def test_queue_via_interpreter() -> None:
    Interpreter().run_source("q = Queue()\nq.put(1)\nq.get().print()")
