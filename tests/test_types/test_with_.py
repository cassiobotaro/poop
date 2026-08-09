import contextlib

import pytest

from poop.types.none import none
from poop.types.with_ import With


class _FakeContextManager:
    """Simple context manager for testing — records calls."""

    def __init__(self, value: object = "resource") -> None:
        self.value = value
        self.entered = False
        self.exited = False
        self.exit_args: tuple[object, object, object] = (None, None, None)

    def __enter__(self) -> object:
        self.entered = True
        return self.value

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        self.exited = True
        self.exit_args = (exc_type, exc_val, exc_tb)
        return False  # do not suppress exceptions


class _SuppressingContextManager(_FakeContextManager):
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> bool:
        super().__exit__(exc_type, exc_val, exc_tb)
        return True  # suppress all exceptions


def test_with_executes_body() -> None:
    log: list[object] = []
    cm = _FakeContextManager("file")
    With(lambda: cm).do(lambda f: log.append(f))
    assert log == ["file"]


def test_with_calls_enter() -> None:
    cm = _FakeContextManager()
    With(lambda: cm).do(lambda _: None)
    assert cm.entered is True


def test_with_calls_exit_on_success() -> None:
    cm = _FakeContextManager()
    With(lambda: cm).do(lambda _: None)
    assert cm.exited is True
    assert cm.exit_args == (None, None, None)


def test_with_calls_exit_on_exception() -> None:
    cm = _FakeContextManager()
    with pytest.raises(ValueError):
        With(lambda: cm).do(lambda _: (_ for _ in ()).throw(ValueError("boom")))
    assert cm.exited is True
    assert cm.exit_args[0] is ValueError


def test_with_reraises_exception_when_exit_returns_false() -> None:
    cm = _FakeContextManager()
    with pytest.raises(RuntimeError, match="oops"):
        With(lambda: cm).do(lambda _: (_ for _ in ()).throw(RuntimeError("oops")))


def test_with_suppresses_exception_when_exit_returns_true() -> None:
    cm = _SuppressingContextManager()
    With(lambda: cm).do(lambda _: (_ for _ in ()).throw(ValueError("suppressed")))
    assert cm.exited is True


def test_with_passes_enter_value_to_body() -> None:
    received: list[object] = []
    cm = _FakeContextManager(value=42)
    With(lambda: cm).do(lambda v: received.append(v))
    assert received == [42]


def test_with_cm_block_is_lazy() -> None:
    created: list[bool] = []

    def make_cm() -> _FakeContextManager:
        created.append(True)
        return _FakeContextManager()

    w = With(make_cm)
    assert created == []  # not created yet
    w.do(lambda _: None)
    assert created == [True]


def test_with_answers_the_body_value() -> None:
    # `do` used to answer the With itself "for chaining", but `do` is the only
    # message With has — there was never anything to chain onto.
    cm = _FakeContextManager()
    assert With(lambda: cm).do(lambda _: 42) == 42


def test_with_answers_none_when_exit_suppresses_the_exception() -> None:
    # __exit__ swallowed the error, so the body never produced a value to
    # answer; Python's `with` just carries on past the block here.
    class _Suppressing:
        def __enter__(self) -> str:
            return "resource"

        def __exit__(self, *_: object) -> bool:
            return True

    def _boom(_: object) -> object:
        raise ValueError("boom")

    assert With(lambda: _Suppressing()).do(_boom) is none


def test_with_str() -> None:
    assert str(With(lambda: None)) == "With"


def test_with_repr() -> None:
    assert repr(With(lambda: None)) == "With"


def test_with_contextlib_closing() -> None:
    log: list[str] = []

    class Resource:
        def close(self) -> None:
            log.append("closed")

    With(lambda: contextlib.closing(Resource())).do(lambda _: log.append("used"))
    assert log == ["used", "closed"]


def test_with_class_does_not_leak_module_path() -> None:
    # `With` keeps its user-facing name but must not expose the internal path.
    assert With.__module__ == "builtins"
    assert repr(With) == "<class 'With'>"


def test_with_cannot_run_twice() -> None:
    import pytest

    from poop.types.with_ import With

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    w = With(lambda: _Ctx())
    w.do(lambda _: None)
    with pytest.raises(RuntimeError, match="already run"):
        w.do(lambda _: None)


def test_with_checks_exit_before_entering() -> None:
    # CPython resolves both slots before entering. Entering first and reaching
    # for the exit half only afterwards ran the acquisition of a manager that
    # could never release it: the side effect happened, and nothing was ever
    # going to undo it.
    import pytest

    from poop.types.with_ import With

    log: list[str] = []

    class _EnterOnly:
        def __enter__(self):
            log.append("entered")
            return self

    with pytest.raises(TypeError, match="it cannot be exited"):
        With(lambda: _EnterOnly()).do(lambda _: log.append("used"))
    assert log == []


def test_with_names_the_protocol_for_a_plain_object() -> None:
    # `AttributeError: __enter__` named a dunder POOP bans everywhere else and
    # said nothing about what the program did wrong.
    import pytest

    from poop.types.int import Int
    from poop.types.with_ import With

    with pytest.raises(TypeError, match="int does not support the context manager"):
        With(lambda: Int(5)).do(lambda _: None)


def test_with_reads_the_protocol_off_the_type_not_the_instance() -> None:
    # A `does_not_understand` hook answering a callable must not be able to
    # forge a context manager: Python's `with` reads both slots off the type.
    import pytest

    from poop.types.object import Object
    from poop.types.with_ import With

    class _Forger(Object):
        __slots__ = ()

        def does_not_understand(self, name: str):
            return lambda *args: None

    with pytest.raises(TypeError, match="it cannot be entered"):
        With(lambda: _Forger()).do(lambda _: None)


def test_with_refuses_a_manager_argument_that_is_not_a_block() -> None:
    # `With` takes a block that *answers* a manager, and passing the manager
    # itself is the obvious first attempt. CPython answered `'C' object is not
    # callable`, which says nothing about what was expected.
    from poop.types.int import Int

    with pytest.raises(TypeError) as info:
        With(Int(5))  # ty: ignore[invalid-argument-type]
    assert str(info.value) == (
        "the manager argument must be a block, got an int — write With(lambda: …)"
    )


def test_with_refuses_a_manager_passed_instead_of_a_block() -> None:
    class Manager:
        def __enter__(self) -> str:
            return "value"

        def __exit__(self, *_: object) -> bool:
            return False

    with pytest.raises(TypeError, match="must be a block"):
        With(Manager())  # ty: ignore[invalid-argument-type]
