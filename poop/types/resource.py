from __future__ import annotations

import resource as _resource
from typing import Any, ClassVar

from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.tuple import Tuple


class RUsage(Object):
    """Wraps Python's `resource.struct_rusage` — process resource usage."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def ru_utime(self) -> Float:
        return Float(self._impl.ru_utime)

    @property
    def ru_stime(self) -> Float:
        return Float(self._impl.ru_stime)

    @property
    def ru_maxrss(self) -> Int:
        return Int(self._impl.ru_maxrss)

    @property
    def ru_ixrss(self) -> Int:
        return Int(self._impl.ru_ixrss)

    @property
    def ru_idrss(self) -> Int:
        return Int(self._impl.ru_idrss)

    @property
    def ru_isrss(self) -> Int:
        return Int(self._impl.ru_isrss)

    @property
    def ru_minflt(self) -> Int:
        return Int(self._impl.ru_minflt)

    @property
    def ru_majflt(self) -> Int:
        return Int(self._impl.ru_majflt)

    @property
    def ru_nswap(self) -> Int:
        return Int(self._impl.ru_nswap)

    @property
    def ru_inblock(self) -> Int:
        return Int(self._impl.ru_inblock)

    @property
    def ru_oublock(self) -> Int:
        return Int(self._impl.ru_oublock)

    @property
    def ru_msgsnd(self) -> Int:
        return Int(self._impl.ru_msgsnd)

    @property
    def ru_msgrcv(self) -> Int:
        return Int(self._impl.ru_msgrcv)

    @property
    def ru_nsignals(self) -> Int:
        return Int(self._impl.ru_nsignals)

    @property
    def ru_nvcsw(self) -> Int:
        return Int(self._impl.ru_nvcsw)

    @property
    def ru_nivcsw(self) -> Int:
        return Int(self._impl.ru_nivcsw)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


def _const(name: str) -> Int | NoneClass:
    """Some `RLIMIT_*` constants are platform-specific; return `Int`
    when present, POOP `none` otherwise."""
    value = getattr(_resource, name, None)
    return none if value is None else Int(value)


class Resource:
    """Namespace mirroring Python's `resource` module — process limits
    and rusage.

    Limit pairs are `Tuple(Int, Int)` of `(soft, hard)`. Constants
    that don't exist on the current platform are bound to `none` (use
    `is_none()` to check before passing them to `getrlimit`).
    """

    RUsage: ClassVar[type[RUsage]] = RUsage

    # Resource categories (subset is platform-specific).
    RLIMIT_CPU: ClassVar[Any] = _const("RLIMIT_CPU")
    RLIMIT_FSIZE: ClassVar[Any] = _const("RLIMIT_FSIZE")
    RLIMIT_DATA: ClassVar[Any] = _const("RLIMIT_DATA")
    RLIMIT_STACK: ClassVar[Any] = _const("RLIMIT_STACK")
    RLIMIT_CORE: ClassVar[Any] = _const("RLIMIT_CORE")
    RLIMIT_RSS: ClassVar[Any] = _const("RLIMIT_RSS")
    RLIMIT_NOFILE: ClassVar[Any] = _const("RLIMIT_NOFILE")
    RLIMIT_OFILE: ClassVar[Any] = _const("RLIMIT_OFILE")
    RLIMIT_AS: ClassVar[Any] = _const("RLIMIT_AS")
    RLIMIT_MEMLOCK: ClassVar[Any] = _const("RLIMIT_MEMLOCK")
    RLIMIT_VMEM: ClassVar[Any] = _const("RLIMIT_VMEM")
    RLIMIT_NPROC: ClassVar[Any] = _const("RLIMIT_NPROC")
    RLIMIT_SBSIZE: ClassVar[Any] = _const("RLIMIT_SBSIZE")
    RLIMIT_SWAP: ClassVar[Any] = _const("RLIMIT_SWAP")
    RLIMIT_NPTS: ClassVar[Any] = _const("RLIMIT_NPTS")
    RLIMIT_LOCKS: ClassVar[Any] = _const("RLIMIT_LOCKS")
    RLIMIT_KQUEUES: ClassVar[Any] = _const("RLIMIT_KQUEUES")
    RLIMIT_MSGQUEUE: ClassVar[Any] = _const("RLIMIT_MSGQUEUE")
    RLIMIT_NICE: ClassVar[Any] = _const("RLIMIT_NICE")
    RLIMIT_RTPRIO: ClassVar[Any] = _const("RLIMIT_RTPRIO")
    RLIMIT_RTTIME: ClassVar[Any] = _const("RLIMIT_RTTIME")
    RLIMIT_SIGPENDING: ClassVar[Any] = _const("RLIMIT_SIGPENDING")

    RLIM_INFINITY: ClassVar[Int] = Int(_resource.RLIM_INFINITY)

    RUSAGE_SELF: ClassVar[Int] = Int(_resource.RUSAGE_SELF)
    RUSAGE_CHILDREN: ClassVar[Int] = Int(_resource.RUSAGE_CHILDREN)
    RUSAGE_THREAD: ClassVar[Any] = _const("RUSAGE_THREAD")
    RUSAGE_BOTH: ClassVar[Any] = _const("RUSAGE_BOTH")

    error: ClassVar[type[Exception]] = _resource.error

    @staticmethod
    def getrlimit(resource: Int, /) -> Tuple:
        soft, hard = _resource.getrlimit(resource._value)
        return Tuple(Int(soft), Int(hard))

    @staticmethod
    def setrlimit(resource: Int, limits: Tuple, /) -> None:
        soft: Any = limits.at(Int(0))
        hard: Any = limits.at(Int(1))
        _resource.setrlimit(resource._value, (soft._value, hard._value))

    @staticmethod
    def prlimit(
        pid: Int,
        resource: Int,
        limits: Tuple | None = None,
        /,
    ) -> Tuple:
        if limits is None:
            soft, hard = _resource.prlimit(pid._value, resource._value)
        else:
            s: Any = limits.at(Int(0))
            h: Any = limits.at(Int(1))
            soft, hard = _resource.prlimit(
                pid._value, resource._value, (s._value, h._value)
            )
        return Tuple(Int(soft), Int(hard))

    @staticmethod
    def getrusage(who: Int) -> RUsage:
        return RUsage(_resource.getrusage(who._value))

    @staticmethod
    def getpagesize() -> Int:
        return Int(_resource.getpagesize())
