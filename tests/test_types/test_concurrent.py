from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.concurrent import (
    CFFuture,
    Concurrent,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def _square(x: int) -> int:
    return x * x


# --- ThreadPoolExecutor ---


def test_threadpool_constructs_default() -> None:
    with ThreadPoolExecutor() as ex:
        assert isinstance(ex, ThreadPoolExecutor)


def test_threadpool_constructs_with_max_workers() -> None:
    with ThreadPoolExecutor(Int(2)) as ex:
        assert isinstance(ex, ThreadPoolExecutor)


def test_threadpool_constructs_with_thread_name_prefix() -> None:
    with ThreadPoolExecutor(Int(2), Str("worker")) as ex:
        assert isinstance(ex, ThreadPoolExecutor)


def test_threadpool_submit_returns_future() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 3)
        assert isinstance(fut, CFFuture)
        assert fut.result() == Int(9)


def test_threadpool_map_returns_list() -> None:
    with ThreadPoolExecutor() as ex:
        result = ex.map(_square, List(Int(1), Int(2), Int(3)))
        # `_square` returns Python ints (no wrapping); the List wraps them.
        assert isinstance(result, List)
        assert result.len() == Int(3)


def test_threadpool_shutdown_returns_none() -> None:
    ex = ThreadPoolExecutor()
    assert ex.shutdown(true, false) is none


# --- ProcessPoolExecutor ---


def test_processpool_constructs() -> None:
    with ProcessPoolExecutor() as ex:
        assert isinstance(ex, ProcessPoolExecutor)


def test_processpool_constructs_with_workers() -> None:
    with ProcessPoolExecutor(Int(2)) as ex:
        assert isinstance(ex, ProcessPoolExecutor)


def test_processpool_submit() -> None:
    with ProcessPoolExecutor(Int(2)) as ex:
        fut = ex.submit(_square, 4)
        assert fut.result(Float(10.0)) == Int(16)


# --- Future ---


def test_future_done_after_result() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        fut.result()
        assert fut.done() is true


def test_future_cancelled_initially_false() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        fut.result()
        assert fut.cancelled() is false


def test_future_running_state() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        # Either running or done at this point.
        from poop.types.boolean import Boolean

        assert isinstance(fut.running(), Boolean)
        fut.result()


def test_future_exception_returns_none_on_success() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        fut.result()
        assert fut.exception() is none


def test_future_exception_with_timeout() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        fut.result()
        assert fut.exception(Float(1.0)) is none


def test_future_cancel_after_done() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        fut.result()
        assert fut.cancel() is false


def test_future_result_with_timeout() -> None:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_square, 5)
        assert fut.result(Float(5.0)) == Int(25)


# --- Module helpers ---


def test_wait_basic() -> None:
    with ThreadPoolExecutor() as ex:
        futs = List(*(ex.submit(_square, i) for i in range(3)))
        pair = Concurrent.wait(futs)
        assert isinstance(pair, Tuple)
        assert pair.len() == Int(2)


def test_wait_with_timeout_and_return_when() -> None:
    with ThreadPoolExecutor() as ex:
        futs = List(*(ex.submit(_square, i) for i in range(3)))
        pair = Concurrent.wait(futs, Float(5.0), Concurrent.ALL_COMPLETED)
        assert isinstance(pair, Tuple)


def test_as_completed_returns_list_of_futures() -> None:
    with ThreadPoolExecutor() as ex:
        futs = List(*(ex.submit(_square, i) for i in range(3)))
        done = Concurrent.as_completed(futs)
        assert isinstance(done, List)


def test_as_completed_with_timeout() -> None:
    with ThreadPoolExecutor() as ex:
        futs = List(*(ex.submit(_square, i) for i in range(3)))
        done = Concurrent.as_completed(futs, Float(5.0))
        assert isinstance(done, List)


# --- Constants and class refs ---


def test_return_when_constants_are_str() -> None:
    assert isinstance(Concurrent.FIRST_COMPLETED, Str)
    assert isinstance(Concurrent.FIRST_EXCEPTION, Str)
    assert isinstance(Concurrent.ALL_COMPLETED, Str)


def test_error_classes() -> None:
    assert issubclass(Concurrent.CancelledError, Exception)
    assert issubclass(Concurrent.TimeoutError, Exception)
    assert issubclass(Concurrent.BrokenExecutor, Exception)
    assert issubclass(Concurrent.InvalidStateError, Exception)


def test_class_refs() -> None:
    assert Concurrent.ThreadPoolExecutor is ThreadPoolExecutor
    assert Concurrent.ProcessPoolExecutor is ProcessPoolExecutor
    assert Concurrent.Future is CFFuture


# --- Interpreter integration ---


def test_concurrent_via_interpreter() -> None:
    Interpreter().run_source("ex = ThreadPoolExecutor()\nex.shutdown()")
