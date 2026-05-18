import signal as _stdlib_signal

import pytest

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.int import Int
from poop.types.none import none
from poop.types.set import Set
from poop.types.signal import Signal
from poop.types.string import Str


def test_signal_constants_are_ints() -> None:
    assert isinstance(Signal.SIGINT, Int)
    assert isinstance(Signal.SIGTERM, Int)
    assert isinstance(Signal.SIGABRT, Int)


def test_signal_constants_match_stdlib() -> None:
    sigint = Signal.SIGINT
    assert isinstance(sigint, Int)
    assert sigint._value == _stdlib_signal.SIGINT


def test_sig_dfl_and_sig_ign_sentinels() -> None:
    assert Signal.SIG_DFL is _stdlib_signal.SIG_DFL
    assert Signal.SIG_IGN is _stdlib_signal.SIG_IGN


def test_signal_signal_round_trip() -> None:
    sigusr1 = Signal.SIGUSR1
    assert isinstance(sigusr1, Int)
    # Save and restore the SIGUSR1 handler.
    old = Signal.signal(sigusr1, Signal.SIG_IGN)
    try:
        assert Signal.getsignal(sigusr1) is Signal.SIG_IGN
    finally:
        Signal.signal(sigusr1, old)


def test_getsignal_returns_handler() -> None:
    sigterm = Signal.SIGTERM
    assert isinstance(sigterm, Int)
    handler = Signal.getsignal(sigterm)
    assert handler is not None


def test_strsignal_returns_str() -> None:
    sigint = Signal.SIGINT
    assert isinstance(sigint, Int)
    result = Signal.strsignal(sigint)
    assert isinstance(result, Str)


def test_strsignal_invalid_raises() -> None:
    with pytest.raises(ValueError):
        Signal.strsignal(Int(99999))


def test_sigpending_returns_set() -> None:
    pending = Signal.sigpending()
    assert isinstance(pending, Set)


@pytest.mark.skipif(
    not hasattr(_stdlib_signal, "raise_signal"),
    reason="raise_signal requires Python 3.8+",
)
def test_raise_signal_returns_none() -> None:
    sigusr1 = Signal.SIGUSR1
    assert isinstance(sigusr1, Int)
    old = Signal.signal(sigusr1, Signal.SIG_IGN)
    try:
        assert Signal.raise_signal(sigusr1) is none
    finally:
        Signal.signal(sigusr1, old)


def test_itimer_constants() -> None:
    # ITIMER_REAL exists on Linux.
    if hasattr(_stdlib_signal, "ITIMER_REAL"):
        assert isinstance(Signal.ITIMER_REAL, Int)


# --- Interpreter integration ---


def test_signal_constants_via_interpreter() -> None:
    Interpreter().run_source("signal.SIGINT.print()")


# --- signal.signal handler bridge ---


def test_signal_accepts_block_handler() -> None:
    seen: list[Int] = []

    def handler(signum: Int, frame: object) -> None:
        seen.append(signum)

    sigusr1 = Signal.SIGUSR1
    if isinstance(sigusr1, type(none)):
        pytest.skip("SIGUSR1 unavailable on this platform")
    previous = Signal.signal(sigusr1, Block(handler))
    try:
        Signal.raise_signal(sigusr1)
        assert seen and isinstance(seen[0], Int)
        assert seen[0] == sigusr1
    finally:
        Signal.signal(sigusr1, previous)


def test_signal_sigign_pass_through() -> None:
    sigusr2 = Signal.SIGUSR2
    if isinstance(sigusr2, type(none)):
        pytest.skip("SIGUSR2 unavailable on this platform")
    previous = Signal.signal(sigusr2, Signal.SIG_IGN)
    try:
        # Should not raise — handler was SIG_IGN.
        Signal.raise_signal(sigusr2)
    finally:
        Signal.signal(sigusr2, previous)


# --- POSIX sig-* extras ---


def test_siginterrupt_returns_none() -> None:
    sigusr1 = Signal.SIGUSR1
    if isinstance(sigusr1, type(none)):
        pytest.skip("SIGUSR1 unavailable on this platform")
    assert Signal.siginterrupt(sigusr1, True) is none
    # restore default behaviour
    Signal.siginterrupt(sigusr1, False)


def test_pthread_sigmask_round_trip() -> None:
    import platform

    if platform.system() == "Windows":
        pytest.skip("pthread_sigmask is POSIX-only")
    sigusr1 = Signal.SIGUSR1
    if isinstance(sigusr1, type(none)):
        pytest.skip("SIGUSR1 unavailable on this platform")
    from poop.types.set import Set

    prev = Signal.pthread_sigmask(Signal.SIG_BLOCK, Set(sigusr1))  # ty: ignore[invalid-argument-type]
    assert isinstance(prev, Set)
    # Unblock again to restore.
    Signal.pthread_sigmask(Signal.SIG_UNBLOCK, Set(sigusr1))  # ty: ignore[invalid-argument-type]


def test_sig_block_constants() -> None:
    import platform

    if platform.system() == "Windows":
        pytest.skip("SIG_BLOCK constants are POSIX-only")
    assert isinstance(Signal.SIG_BLOCK, Int)
    assert isinstance(Signal.SIG_UNBLOCK, Int)
    assert isinstance(Signal.SIG_SETMASK, Int)
