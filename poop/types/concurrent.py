from __future__ import annotations

import concurrent.futures as _cf
from typing import Any, ClassVar, Self

from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _opt_timeout(timeout: Float | Int | None) -> Any:
    return None if timeout is None else timeout._value


class CFFuture(Object):
    """Wraps `concurrent.futures.Future`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def result(self, timeout: Float | Int | None = None) -> Any:
        return self._impl.result(_opt_timeout(timeout))

    def exception(self, timeout: Float | Int | None = None) -> Any:
        result = self._impl.exception(_opt_timeout(timeout))
        return none if result is None else result

    def cancel(self) -> Boolean:
        return true if self._impl.cancel() else false

    def cancelled(self) -> Boolean:
        return true if self._impl.cancelled() else false

    def done(self) -> Boolean:
        return true if self._impl.done() else false

    def running(self) -> Boolean:
        return true if self._impl.running() else false


class _BaseExecutor(Object):
    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> CFFuture:
        return CFFuture(self._impl.submit(fn, *args, **kwargs))

    def map(self, fn: Any, iterable: List) -> List:
        py_list = list(iterable) if isinstance(iterable, List) else iterable
        return List(*self._impl.map(fn, py_list))

    def shutdown(
        self,
        wait: Boolean | None = None,
        cancel_futures: Boolean | None = None,
    ) -> NoneClass:
        w = True if wait is None else bool(wait)
        cf = False if cancel_futures is None else bool(cancel_futures)
        self._impl.shutdown(wait=w, cancel_futures=cf)
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.shutdown(wait=True)


class ThreadPoolExecutor(_BaseExecutor):
    """Wraps `concurrent.futures.ThreadPoolExecutor`."""

    def __init__(
        self,
        max_workers: Int | None = None,
        thread_name_prefix: Str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if max_workers is not None:
            kwargs["max_workers"] = max_workers._value
        if thread_name_prefix is not None:
            kwargs["thread_name_prefix"] = thread_name_prefix._value
        super().__init__(_cf.ThreadPoolExecutor(**kwargs))


class ProcessPoolExecutor(_BaseExecutor):
    """Wraps `concurrent.futures.ProcessPoolExecutor`."""

    def __init__(self, max_workers: Int | None = None) -> None:
        kwargs: dict[str, Any] = {}
        if max_workers is not None:
            kwargs["max_workers"] = max_workers._value
        super().__init__(_cf.ProcessPoolExecutor(**kwargs))


class Concurrent:
    """Namespace mirroring Python's `concurrent.futures` module."""

    ThreadPoolExecutor: ClassVar[type[ThreadPoolExecutor]] = ThreadPoolExecutor
    ProcessPoolExecutor: ClassVar[type[ProcessPoolExecutor]] = ProcessPoolExecutor
    Future: ClassVar[type[CFFuture]] = CFFuture

    # Return-when constants
    FIRST_COMPLETED: ClassVar[Str] = Str(_cf.FIRST_COMPLETED)
    FIRST_EXCEPTION: ClassVar[Str] = Str(_cf.FIRST_EXCEPTION)
    ALL_COMPLETED: ClassVar[Str] = Str(_cf.ALL_COMPLETED)

    # Errors
    CancelledError: ClassVar[type[BaseException]] = _cf.CancelledError
    TimeoutError: ClassVar[type[BaseException]] = _cf.TimeoutError
    BrokenExecutor: ClassVar[type[BaseException]] = _cf.BrokenExecutor
    InvalidStateError: ClassVar[type[BaseException]] = _cf.InvalidStateError

    @staticmethod
    def wait(
        futures: List,
        timeout: Float | Int | None = None,
        return_when: Str | None = None,
    ) -> Tuple:
        impls = [f._impl for f in futures if isinstance(f, CFFuture)]
        kwargs: dict[str, Any] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout._value
        if return_when is not None:
            kwargs["return_when"] = return_when._value
        done, not_done = _cf.wait(impls, **kwargs)
        return Tuple(
            List(*(CFFuture(f) for f in done)),
            List(*(CFFuture(f) for f in not_done)),
        )

    @staticmethod
    def as_completed(futures: List, timeout: Float | Int | None = None) -> List:
        impls = [f._impl for f in futures if isinstance(f, CFFuture)]
        kwargs: dict[str, Any] = {}
        if timeout is not None:
            kwargs["timeout"] = timeout._value
        return List(*(CFFuture(f) for f in _cf.as_completed(impls, **kwargs)))
