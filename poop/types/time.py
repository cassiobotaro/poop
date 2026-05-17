from __future__ import annotations

import time as _time
from typing import Any, ClassVar

from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


class StructTime(Object):
    """Wraps Python's `time.struct_time` — nine-tuple of time components."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def tm_year(self) -> Int:
        return Int(self._impl.tm_year)

    @property
    def tm_mon(self) -> Int:
        return Int(self._impl.tm_mon)

    @property
    def tm_mday(self) -> Int:
        return Int(self._impl.tm_mday)

    @property
    def tm_hour(self) -> Int:
        return Int(self._impl.tm_hour)

    @property
    def tm_min(self) -> Int:
        return Int(self._impl.tm_min)

    @property
    def tm_sec(self) -> Int:
        return Int(self._impl.tm_sec)

    @property
    def tm_wday(self) -> Int:
        return Int(self._impl.tm_wday)

    @property
    def tm_yday(self) -> Int:
        return Int(self._impl.tm_yday)

    @property
    def tm_isdst(self) -> Int:
        return Int(self._impl.tm_isdst)

    @property
    def tm_zone(self) -> Str | NoneClass:
        z = getattr(self._impl, "tm_zone", None)
        return none if z is None else Str(z)

    @property
    def tm_gmtoff(self) -> Int | NoneClass:
        g = getattr(self._impl, "tm_gmtoff", None)
        return none if g is None else Int(g)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class Time:
    """Namespace mirroring Python's `time` module."""

    StructTime: ClassVar[type[StructTime]] = StructTime

    @staticmethod
    def time() -> Float:
        return Float(_time.time())

    @staticmethod
    def time_ns() -> Int:
        return Int(_time.time_ns())

    @staticmethod
    def monotonic() -> Float:
        return Float(_time.monotonic())

    @staticmethod
    def monotonic_ns() -> Int:
        return Int(_time.monotonic_ns())

    @staticmethod
    def perf_counter() -> Float:
        return Float(_time.perf_counter())

    @staticmethod
    def perf_counter_ns() -> Int:
        return Int(_time.perf_counter_ns())

    @staticmethod
    def process_time() -> Float:
        return Float(_time.process_time())

    @staticmethod
    def process_time_ns() -> Int:
        return Int(_time.process_time_ns())

    @staticmethod
    def thread_time() -> Float:
        return Float(_time.thread_time())

    @staticmethod
    def thread_time_ns() -> Int:
        return Int(_time.thread_time_ns())

    @staticmethod
    def sleep(seconds: Float | Int) -> NoneClass:
        _time.sleep(seconds._value)
        return none

    @staticmethod
    def strftime(fmt: Str, t: StructTime | None = None) -> Str:
        if t is None:
            return Str(_time.strftime(fmt._value))
        return Str(_time.strftime(fmt._value, t._impl))

    @staticmethod
    def strptime(s: Str, fmt: Str) -> StructTime:
        return StructTime(_time.strptime(s._value, fmt._value))

    @staticmethod
    def gmtime(secs: Float | Int | None = None) -> StructTime:
        if secs is None:
            return StructTime(_time.gmtime())
        return StructTime(_time.gmtime(secs._value))

    @staticmethod
    def localtime(secs: Float | Int | None = None) -> StructTime:
        if secs is None:
            return StructTime(_time.localtime())
        return StructTime(_time.localtime(secs._value))

    @staticmethod
    def mktime(t: StructTime) -> Float:
        return Float(_time.mktime(t._impl))

    @staticmethod
    def asctime(t: StructTime | None = None) -> Str:
        if t is None:
            return Str(_time.asctime())
        return Str(_time.asctime(t._impl))

    @staticmethod
    def ctime(secs: Float | Int | None = None) -> Str:
        if secs is None:
            return Str(_time.ctime())
        return Str(_time.ctime(secs._value))

    @staticmethod
    def tzname() -> Tuple:
        return Tuple(*(Str(n) for n in _time.tzname))

    @staticmethod
    def timezone() -> Int:
        return Int(_time.timezone)

    @staticmethod
    def altzone() -> Int:
        return Int(_time.altzone)

    @staticmethod
    def daylight() -> Int:
        return Int(_time.daylight)
