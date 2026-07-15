import pytest

from poop.types.error import Error
from poop.types.none import none
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


def test_try_run_twice_raises() -> None:
    calls: list[bool] = []
    t = Try(lambda: calls.append(True))
    t.run()
    assert calls == [True]
    with pytest.raises(RuntimeError, match="already been executed"):
        t.run()
    assert calls == [True]


def test_try_finally_after_run_raises() -> None:
    calls: list[bool] = []
    t = Try(lambda: calls.append(True))
    t.run()
    with pytest.raises(RuntimeError, match="already been executed"):
        t.finally_(lambda: calls.append(False))
    assert calls == [True]


class _Captured:
    """A throwaway object used to probe whether a Try pins a closure."""


def test_try_finally_after_run_does_not_retain_block() -> None:
    # A post-execution finally_ is rejected; it must not pin the cleanup
    # closure on the already-dead Try (single-use drop invariant).
    import gc
    import weakref

    def register_post_run() -> tuple[Try, weakref.ref[_Captured]]:
        t = Try(lambda: None)
        t.run()
        captured = _Captured()
        with pytest.raises(RuntimeError, match="already been executed"):
            t.finally_(lambda: captured)
        return t, weakref.ref(captured)

    t, ref = register_post_run()
    gc.collect()
    assert ref() is None
    assert t._finally_block is None


def test_try_except_after_run_does_not_retain_handler() -> None:
    # Registering a handler after execution is a no-op; it must not pin the
    # handler closure on a Try that can never consume it.
    import gc
    import weakref

    def register_post_run() -> tuple[Try, weakref.ref[_Captured]]:
        t = Try(lambda: None)
        t.run()
        captured = _Captured()
        t.except_(ValueError, lambda e: captured)
        return t, weakref.ref(captured)

    t, ref = register_post_run()
    gc.collect()
    assert ref() is None
    assert t._handlers == []


def test_try_answers_the_protected_block_value() -> None:
    # The whole point of proposal 5: `try: return f()` needs a substitute.
    assert Try(lambda: 42).run() == 42


def test_try_answers_the_handler_value_when_one_fires() -> None:
    # ... and so does `except: return default`.
    result = (
        Try(lambda: _raise(ValueError("bad"))).except_(ValueError, lambda e: -1).run()
    )
    assert result == -1


def test_try_answers_the_block_value_even_when_it_is_none() -> None:
    # POOP's `none` is a value like any other and passes straight through.
    assert Try(lambda: none).run() is none


def test_try_finally_answers_the_block_value_not_the_cleanup_value() -> None:
    # Mirrors Smalltalk's `ensure:`, which answers the protected block.
    assert Try(lambda: 42).finally_(lambda: 99) == 42


def test_try_finally_answers_the_handler_value() -> None:
    calls: list[str] = []
    result = (
        Try(lambda: _raise(ValueError("bad")))
        .except_(ValueError, lambda e: -1)
        .finally_(lambda: calls.append("cleanup"))
    )
    assert result == -1
    assert calls == ["cleanup"]


def test_try_with_no_matching_handler_still_raises() -> None:
    with pytest.raises(KeyError):
        Try(lambda: _raise(KeyError("missing"))).except_(ValueError, lambda e: -1).run()
