import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter

_MANAGERS = """
class Cm(Object):
    async def __aenter__(self):
        "enter".print()
        return "resource"

    async def __aexit__(self, kind, error, traceback):
        kind.is_none().if_true_if_false(
            lambda: "exit".print(), lambda: kind.name().print()
        )

class Forgiving(Cm):
    async def __aexit__(self, kind, error, traceback):
        "forgiven".print()
        return True

class Page(Object):
    async def body(self, resource):
        ("body " + resource).print()
        return 1

    async def fails(self, resource):
        ValueError.raise_("x")
"""


def _in_main(body: str) -> str:
    return (
        f"{_MANAGERS}class Main(Page):\n"
        "    async def main(self):\n"
        f"        {body}\n"
        "Async.run(Main().main())\n"
    )


def _printed(source: str, capsys: pytest.CaptureFixture[str]) -> str:
    Interpreter().run_source(source)
    return capsys.readouterr().out


def _refusal(source: str) -> str:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source)
    return str(info.value)


@pytest.mark.parametrize(
    ("args", "given"), [("", "nothing"), ("lambda: 1, lambda: 2", "2 arguments")]
)
def test_async_with_counts_its_arguments(args: str, given: str) -> None:
    assert (
        f"TypeError: AsyncWith takes one block, got {given} — write "
        "AsyncWith(lambda: …)"
    ) in _refusal(f"AsyncWith({args})")


def test_nothing_runs_before_the_await(capsys: pytest.CaptureFixture[str]) -> None:
    source = f"{_MANAGERS}AsyncWith(lambda: Cm()).do(lambda r: Page().body(r))\n"
    with pytest.warns(RuntimeWarning, match="never awaited"):
        assert _printed(source, capsys) == ""


def test_the_body_runs_inside_the_manager(capsys: pytest.CaptureFixture[str]) -> None:
    body = "AsyncWith(lambda: Cm()).do(lambda r: self.body(r)).await_().print()"
    assert _printed(_in_main(body), capsys) == "enter\nbody resource\nexit\n1\n"


def test_a_failure_at_the_body_s_await_reaches_the_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = "AsyncWith(lambda: Cm()).do(lambda r: self.fails(r)).await_()"
    with pytest.raises(PoopError, match="ValueError: x"):
        Interpreter().run_source(_in_main(body))
    assert capsys.readouterr().out == "enter\nValueError\n"


def test_an_exit_answering_true_swallows_the_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = (
        "AsyncWith(lambda: Forgiving()).do(lambda r: self.fails(r))"
        ".await_().is_none().print()"
    )
    assert _printed(_in_main(body), capsys) == "enter\nforgiven\nTrue\n"


def test_a_manager_without_the_protocol_is_refused_before_entering() -> None:
    body = "AsyncWith(lambda: 5).do(lambda r: self.body(r)).await_()"
    assert (
        "TypeError: int does not support the asynchronous context manager protocol "
        "— it cannot be entered"
    ) in _refusal(_in_main(body))


def test_a_synchronous_manager_is_refused() -> None:
    source = (
        "class Sync(Object):\n"
        "    def __enter__(self):\n"
        "        return self\n"
        "    def __exit__(self, kind, error, traceback):\n"
        "        pass\n"
        + _in_main("AsyncWith(lambda: Sync()).do(lambda r: self.body(r)).await_()")
    )
    assert "Sync does not support the asynchronous context manager protocol" in (
        _refusal(source)
    )


def test_a_body_that_does_not_await_is_refused_after_the_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = "AsyncWith(lambda: Cm()).do(lambda r: 1).await_()"
    assert (
        "TypeError: the AsyncWith body must answer a coroutine, got an int — use "
        "With for a body that does not await"
    ) in _refusal(_in_main(body))
    assert capsys.readouterr().out == "enter\nexit\n"


def test_a_body_that_is_not_a_block_is_refused() -> None:
    assert "write .do(lambda resource: …)" in _refusal(
        f"{_MANAGERS}AsyncWith(lambda: Cm()).do(5)\n"
    )


def test_running_twice_is_refused() -> None:
    body = (
        "w = AsyncWith(lambda: Cm())\n"
        "        w.do(lambda r: self.body(r)).await_()\n"
        "        w.do(lambda r: self.body(r))"
    )
    assert (
        "RuntimeError: AsyncWith has already run; create a new AsyncWith instance "
        "to run again."
    ) in _refusal(_in_main(body))
