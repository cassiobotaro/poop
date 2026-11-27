import asyncio
import re
from functools import partial
from typing import Any

import pytest

from poop.errors import PoopError
from poop.executor import execute
from poop.interpreter import Interpreter
from poop.transformers.await_ import AwaitTransformer
from poop.types.boolean import true
from tests._support import rewritten

_rewritten = partial(rewritten, AwaitTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("c.await_()", "await c"),
        ("c.a().await_().b().await_()", "await (await c.a()).b()"),
        ("c.await_().print()", "(await c).print()"),
        # Any other message is left alone.
        ("c.wait()", "c.wait()"),
    ],
    ids=["bare", "chained", "then_a_message", "another_message"],
)
def test_await_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


_PROGRAM = """
class Client(Object):
    async def get(self, x):
        return x

class Page(Object):
    async def fetch(self):
        return "ok"

    async def client(self):
        return Client()

    async def a(self):
        return "a"

    async def b(self):
        return "b"

    async def fetched(self):
        return self.fetch().await_()

    async def chained(self):
        return self.client().await_().get("x").await_()

    async def either(self, flag):
        return flag.if_true_if_false(lambda: self.a(), lambda: self.b()).await_()
"""


def _page() -> Any:
    interpreter = Interpreter()
    namespace = interpreter.new_namespace()
    execute(interpreter.transform_source(_PROGRAM), namespace=namespace)
    page: Any = namespace["Page"]
    return page()


@pytest.mark.parametrize(
    ("method", "args", "expected"),
    [("fetched", (), "ok"), ("chained", (), "x"), ("either", (true,), "a")],
    ids=["a method's answer", "chained left to right", "a conditional await"],
)
def test_await_answers_the_awaited_value(
    method: str, args: tuple[object, ...], expected: str
) -> None:
    assert str(asyncio.run(getattr(_page(), method)(*args))) == expected


_UNAWAITABLE = """
class Page(Object):
    def sync(self):
        return 1

    async def bad(self):
        return self.sync().await_()

    async def caught(self):
        return Try(lambda: self.bad()).except_(
            TypeError, lambda e: e.message()
        ).await_()
"""

_SENTENCE = (
    "int cannot be awaited — send #await_ to a coroutine, the value an async "
    "method answers"
)


def test_a_receiver_that_cannot_be_awaited_is_refused_in_poop_s_words() -> None:
    with pytest.raises(PoopError, match=f"TypeError: {re.escape(_SENTENCE)}"):
        Interpreter().run_source(f"{_UNAWAITABLE}Async.run(Page().bad())\n")


def test_the_refusal_reads_the_same_when_caught(
    capsys: pytest.CaptureFixture[str],
) -> None:
    Interpreter().run_source(f"{_UNAWAITABLE}Async.run(Page().caught()).print()\n")
    assert capsys.readouterr().out == f"{_SENTENCE}\n"
