import asyncio
from functools import partial
from typing import Any

import pytest

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
