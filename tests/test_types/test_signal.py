import signal as _stdlib_signal

import pytest

from poop.interpreter import Interpreter
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
