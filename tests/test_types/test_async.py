import contextlib
import gc
import re
import time
import warnings
from typing import TYPE_CHECKING

import pytest

from poop.errors import ExecutionError, ValidationError
from poop.interpreter import Interpreter

if TYPE_CHECKING:
    from collections.abc import Generator

_PAGE = """
class Page(Object):
    async def a(self):
        Async.sleep(0.02).await_()
        return 1

    async def b(self):
        Async.sleep(0.01).await_()
        return 2

    async def double(self, n):
        return n * 2

    async def slow(self):
        Async.sleep(0.1).await_()

    async def fails(self):
        ValueError.raise_("boom")

    async def answer(self):
        return 42

"""


def _program(source: str, capsys: pytest.CaptureFixture[str]) -> str:
    Interpreter().run_source(_PAGE + source)
    return capsys.readouterr().out


def _in_main(body: str) -> str:
    return (
        "class Main(Page):\n"
        "    async def main(self):\n"
        f"        {body}\n"
        "\n"
        "Async.run(Main().main())\n"
    )


@contextlib.contextmanager
def _no_unawaited_warning() -> Generator[None]:
    """Fail if a coroutine handed to a refused send warns that it was never
    awaited. The refusal's traceback holds the coroutine in a cycle, so it is
    collected here rather than in whichever test runs next."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        yield
        gc.collect()
    assert [str(w.message) for w in caught if w.category is RuntimeWarning] == []


def _refusal(source: str) -> str:
    with pytest.raises(ExecutionError) as exc_info:
        Interpreter().run_source(_PAGE + source)
    return str(exc_info.value)


def test_async_is_named_async(capsys: pytest.CaptureFixture[str]) -> None:
    assert _program("Async.name().print()", capsys) == "Async\n"


def test_async_has_no_instances() -> None:
    assert (
        "TypeError: Async has no instances — send run, sleep, gather or timeout to the class"
        in (_refusal("Async()"))
    )


def test_async_cannot_be_shadowed() -> None:
    with pytest.raises(ValidationError):
        Interpreter().run_source("Async = 1")


def test_run_answers_the_coroutine_value(capsys: pytest.CaptureFixture[str]) -> None:
    assert _program("Async.run(Page().answer()).print()", capsys) == "42\n"


def test_run_refuses_what_cannot_be_awaited() -> None:
    assert "TypeError: #run expects a coroutine, got an int" in _refusal("Async.run(5)")


def test_run_inside_run_fails_as_cpython_does() -> None:
    with _no_unawaited_warning():
        refusal = _refusal(_in_main("Async.run(self.answer())"))
    assert (
        "RuntimeError: asyncio.run() cannot be called from a running event loop"
        in refusal
    )


def test_sleep_answers_none_by_default(capsys: pytest.CaptureFixture[str]) -> None:
    out = _program(_in_main("Async.sleep(0).await_().is_none().print()"), capsys)
    assert out == "True\n"


def test_sleep_answers_its_result(capsys: pytest.CaptureFixture[str]) -> None:
    assert _program(_in_main('Async.sleep(0, "done").await_().print()'), capsys) == (
        "done\n"
    )


@pytest.mark.parametrize(
    ("delay", "kind"), [('"1"', "a str"), ("True", "a bool"), ("None", "a NoneType")]
)
def test_sleep_refuses_a_delay_that_is_not_a_number(delay: str, kind: str) -> None:
    assert f"TypeError: #sleep expects a number, got {kind}" in _refusal(
        f"Async.sleep({delay})"
    )


def test_gather_answers_a_list_in_the_order_given(
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = "Async.gather(self.a(), self.b()).await_().repr().print()"
    assert _program(_in_main(body), capsys) == "[1, 2]\n"


def test_gather_takes_a_mapped_collection(capsys: pytest.CaptureFixture[str]) -> None:
    body = "Async.gather(*[1, 2].map(lambda n: self.double(n))).await_().repr().print()"
    assert _program(_in_main(body), capsys) == "[2, 4]\n"


def test_gather_runs_its_coroutines_concurrently(
    capsys: pytest.CaptureFixture[str],
) -> None:
    started = time.monotonic()
    _program(
        _in_main("Async.gather(self.slow(), self.slow(), self.slow()).await_()"), capsys
    )
    assert time.monotonic() - started < 0.25


def test_gather_propagates_the_first_failure() -> None:
    assert "ValueError: boom" in _refusal(
        _in_main("Async.gather(self.answer(), self.fails()).await_()")
    )


def test_gather_refuses_what_cannot_be_awaited() -> None:
    with _no_unawaited_warning():
        refusal = _refusal("Async.gather(Page().answer(), 5)")
    assert re.search(r"TypeError: #gather expects coroutines, got an int", refusal)
