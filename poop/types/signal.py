from __future__ import annotations

import signal as _signal
from typing import Any, ClassVar

from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.set import Set
from poop.types.string import Str


def _as_handler(handler: Any) -> Any:
    """Accept either Python callable, POOP Block, or signal sentinel."""
    if handler is _signal.SIG_DFL or handler is _signal.SIG_IGN:
        return handler
    return handler


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
    def signal(signalnum: Int, handler: Any) -> Any:
        return _signal.signal(signalnum._value, _as_handler(handler))

    @staticmethod
    def getsignal(signalnum: Int) -> Any:
        return _signal.getsignal(signalnum._value)

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
