import ast

import pytest

from poop.validators.no_misplaced_await import NoMisplacedAwaitValidator

_NOT_ASYNC = "'await' outside async function — send await_() inside an async def method"
_IN_BLOCK = (
    "'await' outside async function — a block cannot await; let it answer the "
    "coroutine and send await_() to that answer"
)


def _messages(source: str) -> list[str]:
    return [e.message for e in NoMisplacedAwaitValidator().collect(ast.parse(source))]


def _in_async_method(body: str) -> str:
    return f"class P:\n    async def m(self, c, ok):\n        {body}\n"


def test_await_inside_an_async_method_passes() -> None:
    assert _messages(_in_async_method("c.await_()")) == []


def test_a_chain_of_awaits_passes() -> None:
    assert _messages(_in_async_method("c.a().await_().b().await_()")) == []


def test_a_block_answering_a_coroutine_awaited_outside_passes() -> None:
    source = _in_async_method("ok.if_true(lambda: self.f()).await_()")
    assert _messages(source) == []


@pytest.mark.parametrize(
    "source",
    [
        "obj.fetch().await_()",
        "class P:\n    def m(self):\n        self.fetch().await_()\n",
        "class P:\n    async def m(self):\n        class Q:\n            x = c.await_()\n",
    ],
    ids=["module level", "a synchronous method", "a class body"],
)
def test_await_outside_an_async_method(source: str) -> None:
    assert _messages(source) == [_NOT_ASYNC]


def test_await_inside_a_block() -> None:
    source = _in_async_method("ok.if_true(lambda: self.fetch().await_())")
    assert _messages(source) == [_IN_BLOCK]


def test_await_inside_a_block_inside_a_synchronous_method() -> None:
    source = "class P:\n    def m(self, ok):\n        ok.if_true(lambda: c.await_())\n"
    assert _messages(source) == [_IN_BLOCK]


@pytest.mark.parametrize(
    ("call", "given"), [("c.await_(1)", 1), ("c.await_(1, k=2)", 2)]
)
def test_await_with_arguments(call: str, given: int) -> None:
    assert _messages(_in_async_method(call)) == [
        f"await_() takes no arguments ({given} given)"
    ]


def test_await_read_without_being_sent() -> None:
    assert _messages(_in_async_method("f = c.await_")) == [
        "await_ is a message — send it: x.await_()"
    ]


@pytest.mark.parametrize("keyword", ["def", "async def"])
def test_a_method_named_await_is_reserved(keyword: str) -> None:
    source = f"class P:\n    {keyword} await_(self):\n        pass\n"
    assert _messages(source) == [
        "await_ is reserved — POOP sends it to await a coroutine; "
        "name the method something else"
    ]


def test_a_misplaced_await_inside_the_receiver_is_still_found() -> None:
    source = _in_async_method("ok.if_true(lambda: c.await_()).await_()")
    assert _messages(source) == [_IN_BLOCK]


def test_error_carries_line_number() -> None:
    errors = NoMisplacedAwaitValidator().collect(ast.parse("x = 1\nc.await_()\n"))
    assert errors[0].lineno == 2
