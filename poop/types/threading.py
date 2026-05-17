from __future__ import annotations

import threading as _threading
from typing import Any, ClassVar, Self

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _opt_timeout
from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


class Thread(_ImplWrapperMixin, Object):
    """Wraps Python's `threading.Thread`."""

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
        self._impl = _threading.Thread(**kwargs)

    def start(self) -> NoneClass:
        self._impl.start()
        return none

    def join(self, timeout: Float | Int | None = None) -> NoneClass:
        self._impl.join(_opt_timeout(timeout))
        return none

    def is_alive(self) -> Boolean:
        return true if self._impl.is_alive() else false

    @property
    def name(self) -> Str:
        return Str(self._impl.name)

    @property
    def ident(self) -> Int | NoneClass:
        return none if self._impl.ident is None else Int(self._impl.ident)

    @property
    def native_id(self) -> Int | NoneClass:
        nid = self._impl.native_id
        return none if nid is None else Int(nid)

    @property
    def daemon(self) -> Boolean:
        return true if self._impl.daemon else false


class Lock(Object):
    """Wraps `threading.Lock` — non-reentrant primitive lock."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _threading.Lock()

    def acquire(
        self, blocking: Boolean | None = None, timeout: Float | Int | None = None
    ) -> Boolean:
        b = True if blocking is None else bool(blocking)
        t = -1 if timeout is None else timeout._value
        return true if self._impl.acquire(b, t) else false

    def release(self) -> NoneClass:
        self._impl.release()
        return none

    def locked(self) -> Boolean:
        return true if self._impl.locked() else false

    def __enter__(self) -> Self:
        self._impl.acquire()
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.release()


class RLock(Object):
    """Wraps `threading.RLock` — reentrant lock."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _threading.RLock()

    def acquire(
        self, blocking: Boolean | None = None, timeout: Float | Int | None = None
    ) -> Boolean:
        b = True if blocking is None else bool(blocking)
        t = -1 if timeout is None else timeout._value
        return true if self._impl.acquire(b, t) else false

    def release(self) -> NoneClass:
        self._impl.release()
        return none

    def __enter__(self) -> Self:
        self._impl.acquire()
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.release()


class Event(Object):
    """Wraps `threading.Event`."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _threading.Event()

    def set(self) -> NoneClass:
        self._impl.set()
        return none

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none

    def is_set(self) -> Boolean:
        return true if self._impl.is_set() else false

    def wait(self, timeout: Float | Int | None = None) -> Boolean:
        return true if self._impl.wait(_opt_timeout(timeout)) else false


class Semaphore(Object):
    """Wraps `threading.Semaphore`."""

    __slots__ = ("_impl",)

    def __init__(self, value: Int | None = None) -> None:
        v = 1 if value is None else value._value
        self._impl = _threading.Semaphore(v)

    def acquire(
        self, blocking: Boolean | None = None, timeout: Float | Int | None = None
    ) -> Boolean:
        b = True if blocking is None else bool(blocking)
        t = None if timeout is None else timeout._value
        return true if self._impl.acquire(b, t) else false

    def release(self) -> NoneClass:
        self._impl.release()
        return none

    def __enter__(self) -> Self:
        self._impl.acquire()
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.release()


class Barrier(Object):
    """Wraps `threading.Barrier`."""

    __slots__ = ("_impl",)

    def __init__(self, parties: Int, timeout: Float | Int | None = None) -> None:
        t = None if timeout is None else timeout._value
        self._impl = _threading.Barrier(parties._value, timeout=t)

    def wait(self, timeout: Float | Int | None = None) -> Int:
        t = None if timeout is None else timeout._value
        return Int(self._impl.wait(t))

    def reset(self) -> NoneClass:
        self._impl.reset()
        return none

    def abort(self) -> NoneClass:
        self._impl.abort()
        return none

    @property
    def parties(self) -> Int:
        return Int(self._impl.parties)

    @property
    def n_waiting(self) -> Int:
        return Int(self._impl.n_waiting)

    @property
    def broken(self) -> Boolean:
        return true if self._impl.broken else false


class Threading:
    """Namespace mirroring Python's `threading` module."""

    Thread: ClassVar[type[Thread]] = Thread
    Lock: ClassVar[type[Lock]] = Lock
    RLock: ClassVar[type[RLock]] = RLock
    Event: ClassVar[type[Event]] = Event
    Semaphore: ClassVar[type[Semaphore]] = Semaphore
    Barrier: ClassVar[type[Barrier]] = Barrier
    BrokenBarrierError: ClassVar[type[BaseException]] = _threading.BrokenBarrierError

    @staticmethod
    def current_thread() -> Thread:
        return Thread._from_impl(_threading.current_thread())

    @staticmethod
    def main_thread() -> Thread:
        return Thread._from_impl(_threading.main_thread())

    @staticmethod
    def active_count() -> Int:
        return Int(_threading.active_count())

    @staticmethod
    def enumerate() -> List:
        return List(*(Thread._from_impl(t) for t in _threading.enumerate()))

    @staticmethod
    def get_ident() -> Int:
        return Int(_threading.get_ident())

    @staticmethod
    def get_native_id() -> Int:
        return Int(_threading.get_native_id())
