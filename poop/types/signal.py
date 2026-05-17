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


def _sig(name: str) -> Int | None:
    val = getattr(_signal, name, None)
    return Int(int(val)) if isinstance(val, int) else None


class Signal:
    """Namespace mirroring Python's `signal` module — OS signal handling."""

    # Sentinel handler values
    SIG_DFL: ClassVar[Any] = _signal.SIG_DFL
    SIG_IGN: ClassVar[Any] = _signal.SIG_IGN

    # Common signal numbers — bind to `none` on platforms where they don't exist.
    SIGABRT: ClassVar[Int | None] = _sig("SIGABRT")
    SIGALRM: ClassVar[Int | None] = _sig("SIGALRM")
    SIGBUS: ClassVar[Int | None] = _sig("SIGBUS")
    SIGCHLD: ClassVar[Int | None] = _sig("SIGCHLD")
    SIGCONT: ClassVar[Int | None] = _sig("SIGCONT")
    SIGFPE: ClassVar[Int | None] = _sig("SIGFPE")
    SIGHUP: ClassVar[Int | None] = _sig("SIGHUP")
    SIGILL: ClassVar[Int | None] = _sig("SIGILL")
    SIGINT: ClassVar[Int | None] = _sig("SIGINT")
    SIGKILL: ClassVar[Int | None] = _sig("SIGKILL")
    SIGPIPE: ClassVar[Int | None] = _sig("SIGPIPE")
    SIGQUIT: ClassVar[Int | None] = _sig("SIGQUIT")
    SIGSEGV: ClassVar[Int | None] = _sig("SIGSEGV")
    SIGSTOP: ClassVar[Int | None] = _sig("SIGSTOP")
    SIGTERM: ClassVar[Int | None] = _sig("SIGTERM")
    SIGTRAP: ClassVar[Int | None] = _sig("SIGTRAP")
    SIGTSTP: ClassVar[Int | None] = _sig("SIGTSTP")
    SIGTTIN: ClassVar[Int | None] = _sig("SIGTTIN")
    SIGTTOU: ClassVar[Int | None] = _sig("SIGTTOU")
    SIGURG: ClassVar[Int | None] = _sig("SIGURG")
    SIGUSR1: ClassVar[Int | None] = _sig("SIGUSR1")
    SIGUSR2: ClassVar[Int | None] = _sig("SIGUSR2")
    SIGWINCH: ClassVar[Int | None] = _sig("SIGWINCH")
    SIGXCPU: ClassVar[Int | None] = _sig("SIGXCPU")
    SIGXFSZ: ClassVar[Int | None] = _sig("SIGXFSZ")

    # Itimer kinds (Unix only — bind to none on platforms missing them)
    ITIMER_REAL: ClassVar[Int | None] = (
        Int(_signal.ITIMER_REAL) if hasattr(_signal, "ITIMER_REAL") else None
    )
    ITIMER_VIRTUAL: ClassVar[Int | None] = (
        Int(_signal.ITIMER_VIRTUAL) if hasattr(_signal, "ITIMER_VIRTUAL") else None
    )
    ITIMER_PROF: ClassVar[Int | None] = (
        Int(_signal.ITIMER_PROF) if hasattr(_signal, "ITIMER_PROF") else None
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
    def pthread_kill(thread_id: Int, signum: Int) -> NoneClass:
        _signal.pthread_kill(thread_id._value, signum._value)
        return none

    @staticmethod
    def sigpending() -> Set:
        return Set(*(Int(s) for s in _signal.sigpending()))
