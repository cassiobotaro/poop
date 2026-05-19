import asyncio as _stdlib_asyncio

import pytest

from poop.interpreter import Interpreter
from poop.types.asyncio import AsyncIO, Future
from poop.types.boolean import false, true
from poop.types.float import Float


async def _coro_returning(n: int) -> int:
    return n


async def _coro_sleep_then_return(n: int) -> int:
    await _stdlib_asyncio.sleep(0)
    return n


def test_run_executes_coroutine() -> None:
    assert AsyncIO.run(_coro_returning(42)) == 42


def test_run_with_debug_flag() -> None:
    assert AsyncIO.run(_coro_returning(7), debug=false) == 7


def test_run_accepts_callable() -> None:
    assert AsyncIO.run(lambda: _coro_returning(99)) == 99


def test_sleep_returns_awaitable() -> None:
    aw = AsyncIO.sleep(Float(0.01))
    try:
        assert hasattr(aw, "__await__") or _stdlib_asyncio.iscoroutine(aw)
    finally:
        if _stdlib_asyncio.iscoroutine(aw):
            aw.close()


def test_sleep_via_run() -> None:
    async def caller() -> int:
        await AsyncIO.sleep(Float(0))
        return 1

    assert AsyncIO.run(caller()) == 1


def test_gather_with_run() -> None:
    async def caller() -> list[int]:
        results = await AsyncIO.gather(
            _coro_returning(1),
            _coro_returning(2),
            _coro_returning(3),
        )
        return results

    assert AsyncIO.run(caller()) == [1, 2, 3]


def test_wait_for_completes() -> None:
    async def caller() -> int:
        return await AsyncIO.wait_for(_coro_sleep_then_return(5), Float(1.0))

    assert AsyncIO.run(caller()) == 5


def test_wait_for_timeout() -> None:
    async def slow() -> int:
        await _stdlib_asyncio.sleep(1.0)
        return 1

    async def caller() -> None:
        await AsyncIO.wait_for(slow(), Float(0.001))

    with pytest.raises(AsyncIO.TimeoutError):
        AsyncIO.run(caller())


def test_shield_with_run() -> None:
    async def caller() -> int:
        return await AsyncIO.shield(_coro_returning(11))

    assert AsyncIO.run(caller()) == 11


def test_create_task_returns_future_inside_loop() -> None:
    async def caller() -> int:
        task = AsyncIO.create_task(_coro_returning(8))
        assert isinstance(task, Future)
        return await task._impl

    assert AsyncIO.run(caller()) == 8


def test_ensure_future_returns_future() -> None:
    async def caller() -> int:
        fut = AsyncIO.ensure_future(_coro_returning(3))
        assert isinstance(fut, Future)
        result = await fut._impl
        assert fut.done() is true
        return result

    assert AsyncIO.run(caller()) == 3


def test_future_cancel_inside_loop() -> None:
    async def caller() -> None:
        fut = AsyncIO.ensure_future(_stdlib_asyncio.sleep(1))
        cancelled = fut.cancel()
        # After cancel, awaiting the future raises CancelledError.
        assert cancelled is true
        try:
            await fut._impl
        except AsyncIO.CancelledError:
            pass

    AsyncIO.run(caller())


def test_asyncio_class_refs() -> None:
    assert AsyncIO.Future is Future


# --- Interpreter integration ---


def test_asyncio_run_via_interpreter() -> None:
    Interpreter().run_source(
        "class Foo:\n"
        "    async def run(self):\n"
        "        await asyncio.sleep(0)\n"
        "        return 42\n"
        "asyncio.run(Foo().run()).print()\n"
    )


# --- D6: AsyncIO.do (async-for substitute) ---


def test_async_do_iterates_sync_block() -> None:
    async def _gen() -> object:
        for i in range(3):
            yield i

    seen: list[int] = []

    async def caller() -> None:
        await AsyncIO.do(_gen(), lambda x: seen.append(x))

    AsyncIO.run(caller())
    assert seen == [0, 1, 2]


def test_async_do_awaits_block_returning_coroutine() -> None:
    async def _gen() -> object:
        for i in range(3):
            yield i

    seen: list[int] = []

    async def _record(x: int) -> None:
        await _stdlib_asyncio.sleep(0)
        seen.append(x)

    async def caller() -> None:
        await AsyncIO.do(_gen(), _record)

    AsyncIO.run(caller())
    assert seen == [0, 1, 2]


def test_async_do_empty_iterable_returns_none() -> None:
    from poop.types.none import none

    async def _empty() -> object:
        if False:
            yield 0

    async def caller() -> object:
        return await AsyncIO.do(_empty(), lambda _: None)

    assert AsyncIO.run(caller()) is none
