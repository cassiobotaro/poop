import asyncio
import re

import pytest

from poop.types import mirrors
from poop.types.coroutine import Coroutine
from poop.types.object import MessageNotUnderstood
from poop.types.string import Str


async def _ok() -> Str:
    return Str("ok")


def _coroutine() -> Coroutine:
    return Coroutine._of(_ok())


def _awaited(coroutine: Coroutine) -> object:
    async def main() -> object:
        return await coroutine

    return asyncio.run(main())


def test_prints_as_coroutine() -> None:
    coroutine = _coroutine()
    assert str(coroutine) == "<coroutine>"
    _awaited(coroutine)


def test_its_class_is_named_coroutine() -> None:
    coroutine = _coroutine()
    assert str(coroutine.class_().name()) == "coroutine"
    _awaited(coroutine)


def test_the_raw_coroutine_attributes_are_unreachable() -> None:
    coroutine = _coroutine()
    with pytest.raises(
        MessageNotUnderstood,
        match=re.escape(
            "coroutine does not understand #cr_frame — try :methods to list its messages"
        ),
    ):
        coroutine.cr_frame  # noqa: B018 — the read is the test
    _awaited(coroutine)


def test_awaiting_answers_the_value() -> None:
    assert str(_awaited(_coroutine())) == "ok"


def test_asyncio_run_and_gather_accept_it() -> None:
    assert str(asyncio.run(_coroutine())) == "ok"

    async def main() -> tuple[object, object]:
        return await asyncio.gather(_coroutine(), _coroutine())

    assert [str(v) for v in asyncio.run(main())] == ["ok", "ok"]


def test_a_second_await_fails_as_cpython_does() -> None:
    coroutine = _coroutine()

    async def main() -> None:
        await coroutine
        await coroutine

    with pytest.raises(
        mirrors.RuntimeError, match="cannot reuse already awaited coroutine"
    ):
        asyncio.run(main())


def test_a_program_cannot_construct_one() -> None:
    with pytest.raises(mirrors.TypeError, match="cannot create 'coroutine' instances"):
        Coroutine()
