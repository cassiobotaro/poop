import pytest

from poop.types.error import Error
from poop.types.int import Int
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


def test_try_class_does_not_leak_module_path() -> None:
    # `Try` keeps its user-facing name but must not expose the internal path.
    assert Try.__module__ == "builtins"
    assert repr(Try) == "<class 'Try'>"


def test_try_refuses_a_protected_argument_that_is_not_a_block() -> None:
    # CPython answered `'int' object is not callable` from one frame inside
    # `run()` — true of every POOP object, and silent about what was wanted.
    with pytest.raises(TypeError) as info:
        Try(Int(5))  # ty: ignore[invalid-argument-type]
    assert str(info.value) == (
        "the protected argument must be a block, got an int — write Try(lambda: …)"
    )


def test_try_refuses_a_handler_that_is_not_a_block() -> None:
    with pytest.raises(TypeError) as info:
        Try(lambda: none).except_(ValueError, Int(5))  # ty: ignore[invalid-argument-type]
    assert str(info.value) == (
        "the handler must be a block, got an int — "
        "write .except_(ValueError, lambda e: …)"
    )


def test_try_refuses_at_construction_not_at_run() -> None:
    """The failure lands where the mistake was written."""
    ran: list[str] = []
    with pytest.raises(TypeError):
        Try(Int(5)).finally_(lambda: ran.append("cleanup"))  # ty: ignore[invalid-argument-type]
    assert ran == []


def test_try_refuses_a_kind_that_is_not_a_class() -> None:
    # The kind used to be stored untouched and first looked at by `isinstance`
    # inside `_execute`, which answered `isinstance() arg 2 must be a type, a
    # tuple of types, or a union` — the banned builtin spelt as the call that
    # replaces it, which proposal 10 closed on all 15 receivers.
    with pytest.raises(TypeError) as info:
        Try(lambda: none).except_(Str("ValueError"), lambda e: none)  # ty: ignore[invalid-argument-type]
    assert str(info.value) == "#except_ expects a class, got a str"


def test_try_refuses_the_kind_where_it_was_written_not_where_it_raised() -> None:
    # Deferring it made the same mistake report or say nothing depending on
    # whether the protected block happened to raise — and saying nothing means
    # the handler the program was relying on was never installed.
    ran: list[str] = []
    with pytest.raises(TypeError, match="#except_ expects a class"):
        Try(lambda: ran.append("protected")).except_(Int(5), lambda e: none)  # ty: ignore[invalid-argument-type]
    assert ran == []


def test_try_refuses_a_class_that_is_no_exception() -> None:
    # A handler that can never fire is a mistake worth naming; CPython refuses
    # `except int` for the same reason.
    from poop.transformers import DEFAULT_NAMESPACE

    with pytest.raises(TypeError) as info:
        Try(lambda: none).except_(DEFAULT_NAMESPACE["_poop_int_cls"], lambda e: none)  # ty: ignore[invalid-argument-type]
    assert str(info.value) == "#except_ catches exception classes, and int is not one"


def test_try_catches_either_of_a_tuple_of_kinds() -> None:
    # Python's own "catch either" spelling: a POOP `Tuple` is a wrapper, so
    # `isinstance` refused it and the spelling was unavailable.
    from poop.types.exceptions import MIRRORS
    from poop.types.tuple import Tuple

    kinds = Tuple(MIRRORS["ValueError"], MIRRORS["ZeroDivisionError"])  # ty: ignore[invalid-argument-type]
    caught = Try(lambda: _raise(MIRRORS["ZeroDivisionError"]("boom"))).except_(
        kinds,  # ty: ignore[invalid-argument-type]
        lambda e: Str("caught"),
    )
    assert caught.run() == Str("caught")


def test_try_refuses_a_tuple_holding_something_that_is_not_a_class() -> None:
    from poop.types.tuple import Tuple

    with pytest.raises(TypeError, match="#except_ catches exception classes"):
        Try(lambda: none).except_(Tuple(Int(5)), lambda e: none)  # ty: ignore[invalid-argument-type]
