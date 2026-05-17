from __future__ import annotations

import multiprocessing as _mp
from typing import Any, ClassVar, Self

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


def _opt_timeout(timeout: Float | Int | None) -> Any:
    return None if timeout is None else timeout._value


class Process(_ImplWrapperMixin, Object):
    """Wraps Python's `multiprocessing.Process`."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        target: Any = None,
        name: Str | None = None,
        daemon: Boolean | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if target is not None:
            kwargs["target"] = target
        if name is not None:
            kwargs["name"] = name._value
        if daemon is not None:
            kwargs["daemon"] = bool(daemon)
        self._impl = _mp.Process(**kwargs)

    def start(self) -> NoneClass:
        self._impl.start()
        return none

    def join(self, timeout: Float | Int | None = None) -> NoneClass:
        self._impl.join(_opt_timeout(timeout))
        return none

    def is_alive(self) -> Boolean:
        return true if self._impl.is_alive() else false

    def terminate(self) -> NoneClass:
        self._impl.terminate()
        return none

    def kill(self) -> NoneClass:
        self._impl.kill()
        return none

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    @property
    def pid(self) -> Int | NoneClass:
        return none if self._impl.pid is None else Int(self._impl.pid)

    @property
    def exitcode(self) -> Int | NoneClass:
        ec = self._impl.exitcode
        return none if ec is None else Int(ec)

    @property
    def name(self) -> Str:
        return Str(self._impl.name)


class MPQueue(Object):
    """Wraps `multiprocessing.Queue`."""

    __slots__ = ("_impl",)

    def __init__(self, maxsize: Int | None = None) -> None:
        m = 0 if maxsize is None else maxsize._value
        self._impl = _mp.Queue(m)

    def put(
        self,
        item: Any,
        block: Boolean | None = None,
        timeout: Float | Int | None = None,
    ) -> NoneClass:
        b = True if block is None else bool(block)
        self._impl.put(item, b, _opt_timeout(timeout))
        return none

    def get(
        self,
        block: Boolean | None = None,
        timeout: Float | Int | None = None,
    ) -> Any:
        b = True if block is None else bool(block)
        return self._impl.get(b, _opt_timeout(timeout))

    def qsize(self) -> Int:
        return Int(self._impl.qsize())

    def empty(self) -> Boolean:
        return true if self._impl.empty() else false

    def full(self) -> Boolean:
        return true if self._impl.full() else false

    def close(self) -> NoneClass:
        self._impl.close()
        return none


class Pool(Object):
    """Wraps Python's `multiprocessing.Pool`."""

    __slots__ = ("_impl",)

    def __init__(self, processes: Int | None = None) -> None:
        p = None if processes is None else processes._value
        self._impl = _mp.Pool(p)

    def apply(self, func: Any, args: Any = None) -> Any:
        if args is None:
            return self._impl.apply(func)
        return self._impl.apply(func, args)

    def map(self, func: Any, iterable: List) -> List:
        py_list = list(iterable) if isinstance(iterable, List) else iterable
        results = self._impl.map(func, py_list)
        return List(*results)

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def terminate(self) -> NoneClass:
        self._impl.terminate()
        return none

    def join(self) -> NoneClass:
        self._impl.join()
        return none

    def __enter__(self) -> Self:
        self._impl.__enter__()
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.__exit__(None, None, None)


class Multiprocessing:
    """Namespace mirroring (a curated subset of) Python's `multiprocessing` module."""

    Process: ClassVar[type[Process]] = Process
    Queue: ClassVar[type[MPQueue]] = MPQueue
    Pool: ClassVar[type[Pool]] = Pool

    @staticmethod
    def cpu_count() -> Int:
        return Int(_mp.cpu_count())

    @staticmethod
    def active_children() -> List:
        return List(*(Process._from_impl(p) for p in _mp.active_children()))

    @staticmethod
    def current_process() -> Process:
        return Process._from_impl(_mp.current_process())

    @staticmethod
    def get_start_method(allow_none: Boolean | None = None) -> Str | NoneClass:
        a = False if allow_none is None else bool(allow_none)
        result = _mp.get_start_method(allow_none=a)
        return none if result is None else Str(result)
