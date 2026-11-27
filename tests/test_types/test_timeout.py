import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter

_PAGE = """
class Page(Object):
    async def report(self, t):
        t.expired().print()
        t.print()
        return "reported"

    async def slow(self):
        return Async.sleep(1).await_()
"""

_LATE = "AsyncWith(lambda: Async.timeout(0.01)).do(lambda t: self.slow())"


def _in_main(body: str) -> str:
    return (
        f"{_PAGE}class Main(Page):\n"
        "    async def main(self):\n"
        f"        {body}\n"
        "Async.run(Main().main())\n"
    )


def _printed(source: str, capsys: pytest.CaptureFixture[str]) -> str:
    Interpreter().run_source(source)
    return capsys.readouterr().out


def _refusal(source: str) -> PoopError:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source)
    return info.value


@pytest.mark.parametrize("delay", ["1", "None"])
def test_a_body_in_time_answers_its_value(
    delay: str, capsys: pytest.CaptureFixture[str]
) -> None:
    body = (
        f"AsyncWith(lambda: Async.timeout({delay}))"
        '.do(lambda t: Async.sleep(0.01, "ok")).await_().print()'
    )
    assert _printed(_in_main(body), capsys) == "ok\n"


def test_a_body_too_late_fails_with_timeout_error() -> None:
    error = _refusal(_in_main(f"{_LATE}.await_()"))
    assert str(error).startswith("TimeoutError")
    assert error.chain == ("caused by CancelledError",)


def test_the_body_receives_the_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    body = "AsyncWith(lambda: Async.timeout(1)).do(lambda t: self.report(t)).await_()"
    assert _printed(_in_main(body), capsys) == "False\n<Timeout>\n"


def test_an_awaited_try_catches_a_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    body = (
        f'Try(lambda: {_LATE}).except_(TimeoutError, lambda e: "late").await_().print()'
    )
    assert _printed(_in_main(body), capsys) == "late\n"


def test_a_timeout_is_caught_by_its_parent(capsys: pytest.CaptureFixture[str]) -> None:
    body = (
        f"Try(lambda: {_LATE}).except_(OSError, lambda e: e.kind().name())"
        ".await_().print()"
    )
    assert _printed(_in_main(body), capsys) == "TimeoutError\n"


def test_a_handler_reads_the_cancellation_as_the_cause(
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = (
        f"Try(lambda: {_LATE}).except_(TimeoutError, "
        "lambda e: e.cause().kind().name()).await_().print()"
    )
    assert _printed(_in_main(body), capsys) == "CancelledError\n"


def test_async_timeout_answers_a_timeout(capsys: pytest.CaptureFixture[str]) -> None:
    assert _printed("Async.timeout(1).class_().name().print()", capsys) == "Timeout\n"


def test_a_delay_of_the_wrong_kind_is_refused() -> None:
    assert "TypeError: #timeout expects a number or None, got a str" in str(
        _refusal('Async.timeout("1")')
    )


def test_a_timeout_is_entered_once() -> None:
    body = (
        "t = Async.timeout(1)\n"
        "        AsyncWith(lambda: t).do(lambda x: Async.sleep(0)).await_()\n"
        "        AsyncWith(lambda: t).do(lambda x: Async.sleep(0)).await_()"
    )
    assert "RuntimeError: Timeout has already been entered" in str(
        _refusal(_in_main(body))
    )


def test_a_timeout_is_not_entered_synchronously() -> None:
    assert (
        "TypeError: Timeout does not support the context manager protocol — it "
        "cannot be entered"
    ) in str(_refusal("With(lambda: Async.timeout(1)).do(lambda t: t)"))


def test_a_program_cannot_construct_one() -> None:
    assert "cannot create 'Timeout' instances — send #timeout to Async" in str(
        _refusal("Async.timeout(1).class_()(1)")
    )
