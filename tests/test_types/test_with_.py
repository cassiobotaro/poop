import contextlib

import pytest

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


def test_with_returns_self_for_chaining() -> None:
    cm = _FakeContextManager()
    w = With(lambda: cm)
    result = w.do(lambda _: None)
    assert result is w


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


# --- D6: AsyncWith ---


class _FakeAsyncContextManager:
    def __init__(self, value: object = "aresource") -> None:
        self.value = value
        self.entered = False
        self.exited = False
        self.exit_args: tuple[object, object, object] = (None, None, None)

    async def __aenter__(self) -> object:
        self.entered = True
        return self.value

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> bool:
        self.exited = True
        self.exit_args = (exc_type, exc_val, exc_tb)
        return False


class _SuppressingAsyncContextManager(_FakeAsyncContextManager):
    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> bool:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        return True


def test_async_with_runs_body_inside_acm() -> None:
    from poop.types.asyncio import AsyncIO
    from poop.types.with_ import AsyncWith

    acm = _FakeAsyncContextManager()
    seen: list[object] = []

    async def caller() -> None:
        await AsyncWith(lambda: acm).do(lambda v: seen.append(v))

    AsyncIO.run(caller())
    assert acm.entered and acm.exited
    assert seen == ["aresource"]


def test_async_with_awaits_async_body() -> None:
    import asyncio as _stdlib_asyncio

    from poop.types.asyncio import AsyncIO
    from poop.types.with_ import AsyncWith

    acm = _FakeAsyncContextManager()
    seen: list[object] = []

    async def _body(v: object) -> None:
        await _stdlib_asyncio.sleep(0)
        seen.append(v)

    async def caller() -> None:
        await AsyncWith(lambda: acm).do(_body)

    AsyncIO.run(caller())
    assert seen == ["aresource"]


def test_async_with_propagates_exceptions() -> None:
    from poop.types.asyncio import AsyncIO
    from poop.types.with_ import AsyncWith

    acm = _FakeAsyncContextManager()

    def _boom(_: object) -> None:
        raise ValueError("nope")

    async def caller() -> None:
        await AsyncWith(lambda: acm).do(_boom)

    with pytest.raises(ValueError, match="nope"):
        AsyncIO.run(caller())
    assert acm.exited


def test_async_with_can_suppress_exceptions() -> None:
    from poop.types.asyncio import AsyncIO
    from poop.types.with_ import AsyncWith

    acm = _SuppressingAsyncContextManager()

    def _boom(_: object) -> None:
        raise ValueError("nope")

    async def caller() -> None:
        await AsyncWith(lambda: acm).do(_boom)

    # No exception escapes because __aexit__ returned True.
    AsyncIO.run(caller())
    assert acm.exited


def test_async_with_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE
    from poop.types.with_ import AsyncWith

    assert DEFAULT_NAMESPACE["AsyncWith"] is AsyncWith
