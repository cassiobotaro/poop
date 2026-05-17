import threading as _stdlib_threading

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.threading import (
    Barrier,
    Event,
    Lock,
    RLock,
    Semaphore,
    Thread,
    Threading,
)

# --- Thread ---


def test_thread_constructs_default() -> None:
    t = Thread()
    assert isinstance(t, Thread)


def test_thread_constructs_with_target() -> None:
    flag: list[bool] = []
    t = Thread(target=lambda: flag.append(True))
    t.start()
    t.join()
    assert flag == [True]


def test_thread_constructs_with_name_and_daemon() -> None:
    t = Thread(name=Str("worker"), daemon=true)
    assert t.name == Str("worker")
    assert t.daemon is true


def test_thread_join_with_timeout() -> None:
    t = Thread(target=lambda: None)
    t.start()
    assert t.join(Float(1.0)) is none


def test_thread_is_alive() -> None:
    t = Thread(target=lambda: None)
    t.start()
    t.join()
    assert isinstance(t.is_alive(), Boolean)


def test_thread_ident_after_start() -> None:
    t = Thread(target=lambda: None)
    t.start()
    t.join()
    assert isinstance(t.ident, Int) or t.ident is none


def test_thread_native_id() -> None:
    t = Thread(target=lambda: None)
    t.start()
    t.join()
    assert isinstance(t.native_id, Int) or t.native_id is none


# --- Lock ---


def test_lock_acquire_release() -> None:
    lock = Lock()
    assert lock.acquire() is true
    assert lock.locked() is true
    assert lock.release() is none
    assert lock.locked() is false


def test_lock_acquire_with_blocking_and_timeout() -> None:
    lock = Lock()
    assert lock.acquire(true, Float(1.0)) is true
    lock.release()


def test_lock_context_manager() -> None:
    lock = Lock()
    with lock:
        assert lock.locked() is true
    assert lock.locked() is false


# --- RLock ---


def test_rlock_acquire_release() -> None:
    lock = RLock()
    assert lock.acquire() is true
    assert lock.release() is none


def test_rlock_acquire_with_timeout() -> None:
    lock = RLock()
    assert lock.acquire(true, Float(1.0)) is true
    lock.release()


def test_rlock_reentrant() -> None:
    lock = RLock()
    lock.acquire()
    assert lock.acquire() is true
    lock.release()
    lock.release()


def test_rlock_context_manager() -> None:
    lock = RLock()
    with lock:
        pass


# --- Event ---


def test_event_set_clear_is_set() -> None:
    e = Event()
    assert e.is_set() is false
    e.set()
    assert e.is_set() is true
    e.clear()
    assert e.is_set() is false


def test_event_wait_with_timeout() -> None:
    e = Event()
    e.set()
    assert e.wait(Float(1.0)) is true


def test_event_wait_no_args_pre_set() -> None:
    e = Event()
    e.set()
    assert e.wait() is true


# --- Semaphore ---


def test_semaphore_default() -> None:
    s = Semaphore()
    assert s.acquire() is true
    s.release()


def test_semaphore_with_value() -> None:
    s = Semaphore(Int(2))
    s.acquire()
    s.acquire()


def test_semaphore_with_blocking_timeout() -> None:
    s = Semaphore(Int(1))
    assert s.acquire(true, Float(1.0)) is true
    s.release()


def test_semaphore_context_manager() -> None:
    s = Semaphore()
    with s:
        pass


# --- Barrier ---


def test_barrier_construct_and_reset() -> None:
    b = Barrier(Int(2))
    assert b.parties == Int(2)
    assert b.reset() is none


def test_barrier_with_timeout() -> None:
    b = Barrier(Int(2), Float(1.0))
    assert isinstance(b, Barrier)


def test_barrier_abort_and_broken() -> None:
    b = Barrier(Int(2))
    assert b.abort() is none
    assert isinstance(b.broken, Boolean)


def test_barrier_n_waiting() -> None:
    b = Barrier(Int(2))
    assert isinstance(b.n_waiting, Int)


# --- Module helpers ---


def test_current_thread() -> None:
    assert isinstance(Threading.current_thread(), Thread)


def test_main_thread() -> None:
    assert isinstance(Threading.main_thread(), Thread)


def test_active_count() -> None:
    assert isinstance(Threading.active_count(), Int)


def test_enumerate_returns_list() -> None:
    assert isinstance(Threading.enumerate(), List)


def test_get_ident() -> None:
    assert isinstance(Threading.get_ident(), Int)


def test_get_native_id() -> None:
    assert isinstance(Threading.get_native_id(), Int)


def test_threading_class_refs() -> None:
    assert Threading.Thread is Thread
    assert Threading.Lock is Lock
    assert Threading.RLock is RLock
    assert Threading.Event is Event
    assert Threading.Semaphore is Semaphore
    assert Threading.Barrier is Barrier


def test_broken_barrier_error_class() -> None:
    assert issubclass(
        Threading.BrokenBarrierError, _stdlib_threading.BrokenBarrierError
    )


# --- Interpreter integration ---


def test_threading_via_interpreter() -> None:
    Interpreter().run_source("threading.get_ident().print()")
