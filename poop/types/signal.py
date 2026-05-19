from __future__ import annotations

import signal as _signal
from typing import Any, ClassVar, cast

from poop.types._bridge import bridge
from poop.types.block import Block
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.set import Set
from poop.types.string import Str


def _sigset_to_raw(sigset: Set) -> set[int]:
    out: set[int] = set()
    for s in sigset._data:
        out.add(cast(Int, s)._value)
    return out


def _siginfo_to_dict(info: Any) -> Dict:
    d = Dict()
    for name in ("si_signo", "si_code", "si_errno", "si_pid", "si_uid", "si_status"):
        if hasattr(info, name):
            d.at_put(Str(name), Int(getattr(info, name)))
    if hasattr(info, "si_band"):
        d.at_put(Str("si_band"), Int(info.si_band))
    return d


def _as_handler(handler: Any) -> Any:
    """Adapt a handler argument for `signal.signal` / friends.

    Signal sentinels (`SIG_DFL`, `SIG_IGN`) pass through untouched.
    `None` (CPython's "no previous handler" placeholder) also passes
    through. POOP `Block`s route through `block.bridge` so the handler
    receives a POOP `Int` signum and a raw Python frame (frame stays
    opaque — POOP has no frame model).
    """
    if handler is None or handler is _signal.SIG_DFL or handler is _signal.SIG_IGN:
        return handler
    if isinstance(handler, Block):
        return bridge(handler)
    return handler


def _wrap_handler(handler: Any) -> Object:
    """Wrap a handler returned by `signal.signal`/`getsignal` for POOP.

    Signal sentinels (`SIG_DFL`, `SIG_IGN`) and `None` (no previous
    handler) flow back to the user unchanged so identity comparisons
    against `Signal.SIG_IGN`/`Signal.SIG_DFL` keep working. Plain
    callables also pass through — POOP has no first-class wrapper for
    arbitrary function objects.
    """
    if (
        handler is None
        or handler is _signal.SIG_DFL
        or handler is _signal.SIG_IGN
        or callable(handler)
    ):
        return handler
    from poop.types._bridge import to_poop

    return to_poop(handler)


def _sig(name: str) -> Int | NoneClass:
    val = getattr(_signal, name, None)
    return Int(int(val)) if isinstance(val, int) else none


class Signal:
    """Namespace mirroring Python's `signal` module — OS signal handling."""

    # Sentinel handler values
    SIG_DFL: ClassVar[Any] = _signal.SIG_DFL
    SIG_IGN: ClassVar[Any] = _signal.SIG_IGN

    # Common signal numbers — bind to POOP `none` on platforms where they don't exist.
    SIGABRT: ClassVar[Int | NoneClass] = _sig("SIGABRT")
    SIGALRM: ClassVar[Int | NoneClass] = _sig("SIGALRM")
    SIGBUS: ClassVar[Int | NoneClass] = _sig("SIGBUS")
    SIGCHLD: ClassVar[Int | NoneClass] = _sig("SIGCHLD")
    SIGCONT: ClassVar[Int | NoneClass] = _sig("SIGCONT")
    SIGFPE: ClassVar[Int | NoneClass] = _sig("SIGFPE")
    SIGHUP: ClassVar[Int | NoneClass] = _sig("SIGHUP")
    SIGILL: ClassVar[Int | NoneClass] = _sig("SIGILL")
    SIGINT: ClassVar[Int | NoneClass] = _sig("SIGINT")
    SIGKILL: ClassVar[Int | NoneClass] = _sig("SIGKILL")
    SIGPIPE: ClassVar[Int | NoneClass] = _sig("SIGPIPE")
    SIGQUIT: ClassVar[Int | NoneClass] = _sig("SIGQUIT")
    SIGSEGV: ClassVar[Int | NoneClass] = _sig("SIGSEGV")
    SIGSTOP: ClassVar[Int | NoneClass] = _sig("SIGSTOP")
    SIGTERM: ClassVar[Int | NoneClass] = _sig("SIGTERM")
    SIGTRAP: ClassVar[Int | NoneClass] = _sig("SIGTRAP")
    SIGTSTP: ClassVar[Int | NoneClass] = _sig("SIGTSTP")
    SIGTTIN: ClassVar[Int | NoneClass] = _sig("SIGTTIN")
    SIGTTOU: ClassVar[Int | NoneClass] = _sig("SIGTTOU")
    SIGURG: ClassVar[Int | NoneClass] = _sig("SIGURG")
    SIGUSR1: ClassVar[Int | NoneClass] = _sig("SIGUSR1")
    SIGUSR2: ClassVar[Int | NoneClass] = _sig("SIGUSR2")
    SIGWINCH: ClassVar[Int | NoneClass] = _sig("SIGWINCH")
    SIGXCPU: ClassVar[Int | NoneClass] = _sig("SIGXCPU")
    SIGXFSZ: ClassVar[Int | NoneClass] = _sig("SIGXFSZ")

    # Itimer kinds (Unix only — bind to POOP none on platforms missing them)
    ITIMER_REAL: ClassVar[Int | NoneClass] = (
        Int(_signal.ITIMER_REAL) if hasattr(_signal, "ITIMER_REAL") else none
    )
    ITIMER_VIRTUAL: ClassVar[Int | NoneClass] = (
        Int(_signal.ITIMER_VIRTUAL) if hasattr(_signal, "ITIMER_VIRTUAL") else none
    )
    ITIMER_PROF: ClassVar[Int | NoneClass] = (
        Int(_signal.ITIMER_PROF) if hasattr(_signal, "ITIMER_PROF") else none
    )

    @staticmethod
    def signal(signalnum: Int, handler: Any) -> Object:
        return _wrap_handler(_signal.signal(signalnum._value, _as_handler(handler)))

    @staticmethod
    def getsignal(signalnum: Int) -> Object:
        return _wrap_handler(_signal.getsignal(signalnum._value))

    @staticmethod
    def strsignal(signalnum: Int) -> Str | NoneClass:
        result = _signal.strsignal(signalnum._value)
        return none if result is None else Str(result)

    @staticmethod
    def raise_signal(signalnum: Int) -> NoneClass:
        _signal.raise_signal(signalnum._value)
        return none

    @staticmethod
    def pthread_kill(thread_id: Int, signalnum: Int, /) -> NoneClass:
        _signal.pthread_kill(thread_id._value, signalnum._value)
        return none

    @staticmethod
    def sigpending() -> Set:
        return Set(*(Int(s) for s in _signal.sigpending()))

    @staticmethod
    def siginterrupt(signalnum: Int, flag: Any) -> NoneClass:
        _signal.siginterrupt(signalnum._value, bool(flag))
        return none

    # Signal-set ops below are POSIX-only — guarded with hasattr so the
    # namespace stays importable on Windows.

    SIG_BLOCK: ClassVar[Int | NoneClass] = (
        Int(_signal.SIG_BLOCK) if hasattr(_signal, "SIG_BLOCK") else none
    )
    SIG_UNBLOCK: ClassVar[Int | NoneClass] = (
        Int(_signal.SIG_UNBLOCK) if hasattr(_signal, "SIG_UNBLOCK") else none
    )
    SIG_SETMASK: ClassVar[Int | NoneClass] = (
        Int(_signal.SIG_SETMASK) if hasattr(_signal, "SIG_SETMASK") else none
    )

    @staticmethod
    def sigwait(sigset: Set) -> Int:
        raw = _sigset_to_raw(sigset)
        return Int(_signal.sigwait(raw))

    @staticmethod
    def pthread_sigmask(how: Int, mask: Set) -> Set:
        prev = _signal.pthread_sigmask(how._value, _sigset_to_raw(mask))
        return Set(*(Int(s) for s in prev))

    @staticmethod
    def sigwaitinfo(sigset: Set) -> Any:
        # Returns a struct_siginfo; flatten the common fields to a POOP
        # Dict so user code can inspect without a sibling wrapper.
        info = _signal.sigwaitinfo(_sigset_to_raw(sigset))
        return _siginfo_to_dict(info)

    @staticmethod
    def sigtimedwait(sigset: Set, timeout: Float | Int) -> Any:
        info = _signal.sigtimedwait(_sigset_to_raw(sigset), timeout._value)
        return none if info is None else _siginfo_to_dict(info)
