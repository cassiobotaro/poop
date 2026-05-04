import pytest

from poop.types.error import Error
from poop.types.string import Str
from poop.types.try_ import Try


def _raise(exc: BaseException) -> None:
    raise exc


def test_try_run_executes_block() -> None:
    called: list[bool] = []
    Try(lambda: called.append(True)).run()
    assert called == [True]


def test_try_finally_executes_block() -> None:
    called: list[bool] = []
    Try(lambda: called.append(True)).finally_()
    assert called == [True]


def test_try_except_handles_matching_exception() -> None:
    received: list[object] = []
    Try(lambda: _raise(ValueError("oops"))).except_(
        ValueError, lambda e: received.append(e)
    ).run()
    assert len(received) == 1
    assert isinstance(received[0], Error)


def test_try_except_handler_receives_error_with_message() -> None:
    received: list[object] = []
    Try(lambda: _raise(ValueError("bad input"))).except_(
        ValueError, lambda e: received.append(e.message())
    ).run()
    assert received == [Str("bad input")]


def test_try_reraises_unmatched_exception() -> None:
    with pytest.raises(TypeError):
        Try(lambda: _raise(TypeError("wrong type"))).except_(
            ValueError, lambda e: None
        ).run()


def test_try_reraises_when_no_handlers() -> None:
    with pytest.raises(KeyError):
        Try(lambda: _raise(KeyError("missing"))).run()


def test_try_finally_always_runs_on_success() -> None:
    log: list[str] = []
    Try(lambda: log.append("block")).finally_(lambda: log.append("finally"))
    assert log == ["block", "finally"]


def test_try_finally_always_runs_on_exception() -> None:
    log: list[str] = []
    Try(lambda: _raise(ValueError("x"))).except_(
        ValueError, lambda e: log.append("handler")
    ).finally_(lambda: log.append("finally"))
    assert log == ["handler", "finally"]


def test_try_finally_runs_before_reraise() -> None:
    log: list[str] = []
    with pytest.raises(ValueError):
        Try(lambda: _raise(ValueError("x"))).finally_(lambda: log.append("finally"))
    assert log == ["finally"]


def test_try_chains_multiple_except() -> None:
    received: list[object] = []
    Try(lambda: _raise(KeyError("k"))).except_(
        ValueError, lambda e: received.append("value")
    ).except_(KeyError, lambda e: received.append("key")).run()
    assert received == ["key"]


def test_try_returns_self_for_chaining() -> None:
    t = Try(lambda: None)
    assert t.except_(ValueError, lambda e: None) is t


def test_try_str() -> None:
    assert str(Try(lambda: None)) == "Try"


def test_try_finally_no_arg_executes_block() -> None:
    called: list[bool] = []
    Try(lambda: called.append(True)).finally_()
    assert called == [True]


def test_try_repr_delegates_to_str() -> None:
    assert repr(Try(lambda: None)) == "Try"
