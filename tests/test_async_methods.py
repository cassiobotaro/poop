"""An `async def` in a class body, awaited: the transformers treat it as a `def`."""

import asyncio
import re
from typing import Any

import pytest

from poop.errors import ValidationError
from poop.executor import execute
from poop.interpreter import Interpreter

_PROGRAM = """
class P(Object):
    async def falls_off(self):
        x = 1

    async def bare(self):
        return

    async def count(self, *args):
        return args.len()

    async def keys(self, **kwargs):
        return kwargs.len()

    async def documented(self):
        "the docstring"
        return 1
"""


def _p() -> Any:
    return _namespace(_PROGRAM)["P"]()


def _printed(line: str, capsys: pytest.CaptureFixture[str]) -> str:
    Interpreter().run_source(f"{_PROGRAM}\n{line}\n")
    return capsys.readouterr().out


def test_sending_runs_nothing_and_awaiting_runs_the_body(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = (
        "class Page(Object):\n"
        "    async def fetch(self):\n"
        '        "ran".print()\n'
        "c = Page().fetch()\n"
        '"sent".print()\n'
        "Async.run(c)\n"
    )
    Interpreter().run_source(source)
    assert capsys.readouterr().out == "sent\nran\n"


def test_an_async_def_outside_a_class_is_refused() -> None:
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "free async functions are forbidden — define methods inside a class "
            "(use a lambda for a local block)"
        ),
    ):
        Interpreter().run_source("async def f():\n    pass\n")


def test_falling_off_the_end_answers_none(capsys: pytest.CaptureFixture[str]) -> None:
    assert _printed("Async.run(P().falls_off()).is_none().print()", capsys) == "True\n"


def test_a_bare_return_answers_none(capsys: pytest.CaptureFixture[str]) -> None:
    assert _printed("Async.run(P().bare()).is_none().print()", capsys) == "True\n"


def test_variadic_positionals_are_a_poop_tuple(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _printed("Async.run(P().count(1, 2)).print()", capsys) == "2\n"


def test_variadic_keywords_are_a_poop_dict(capsys: pytest.CaptureFixture[str]) -> None:
    assert _printed("Async.run(P().keys(a=1)).print()", capsys) == "1\n"


def test_a_docstring_stays_a_docstring() -> None:
    method = type(_p()).__dict__["documented"]
    assert method.__func__.__doc__ == "the docstring"


_REACHED = """
class Base(Object):
    async def fetch(self):
        "fetched".print()
        return "base"

    @staticmethod
    async def shared():
        return "shared"

class Page(Base):
    async def fetch(self):
        return super().fetch()

    async def __call__(self):
        return "called"
"""


def _namespace(source: str) -> dict[str, Any]:
    interpreter = Interpreter()
    namespace = interpreter.new_namespace()
    execute(interpreter.transform_source(source), namespace=namespace)
    return namespace


def _class_name(value: Any) -> str:
    return str(value.class_().name())


def _drained(coroutine: Any) -> Any:
    return asyncio.run(coroutine)


def test_every_way_of_reaching_an_async_method_answers_a_coroutine() -> None:
    namespace = _namespace(_REACHED)
    page = namespace["Page"]()
    base = namespace["Base"]
    reached = [
        page.fetch(),
        page.get_attr("fetch")(),
        page(),
        base.shared(),
    ]
    assert [_class_name(c) for c in reached] == ["coroutine"] * 4
    # Both reads of `Page.fetch` answer the coroutine `super().fetch()` made.
    for coroutine in reached[:2]:
        _drained(_drained(coroutine))
    for coroutine in reached[2:]:
        _drained(coroutine)


def test_super_answers_a_coroutine_the_method_awaits(
    capsys: pytest.CaptureFixture[str],
) -> None:
    page = _namespace(_REACHED)["Page"]()
    inner = _drained(page.fetch())
    assert _class_name(inner) == "coroutine"
    assert capsys.readouterr().out == ""
    assert str(_drained(inner)) == "base"


def test_sending_runs_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    base = _namespace(_REACHED)["Base"]()
    coroutine = base.fetch()
    assert capsys.readouterr().out == ""
    _drained(coroutine)
    assert capsys.readouterr().out == "fetched\n"


def test_an_async_method_is_listed_by_dir() -> None:
    page = _namespace(_REACHED)["Page"]()
    assert "fetch" in [str(name) for name in page.dir()]


def test_a_wrong_count_names_the_method() -> None:
    page = _namespace(_REACHED)["Page"]()
    with pytest.raises(
        TypeError,
        match=re.escape("Page.fetch() takes 1 positional argument but 2 were given"),
    ):
        page.fetch(1)


def test_a_forgotten_await_warns_as_cpython_does() -> None:
    with pytest.warns(
        RuntimeWarning, match=re.escape("coroutine 'Page.fetch' was never awaited")
    ):
        Interpreter().run_source(
            "class Page(Object):\n"
            "    async def fetch(self):\n"
            "        pass\n"
            "Page().fetch()\n"
        )
