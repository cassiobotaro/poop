"""The four lazy views hash by identity, as CPython's `map`/`filter`/`zip`/`enumerate` do.

Each used to re-declare `Object`'s identity `__eq__` without its `__hash__`, and
a class that defines `__eq__` alone gets `__hash__ = None` — so `{xs.map(b)}`
refused a value CPython puts in a set without complaint.
"""

import pytest

from poop.interpreter import Interpreter

_VIEWS = {
    "map": "[1, 2].map(lambda x: x)",
    "filter": "[1, 2].filter(lambda x: True)",
    "zip": "[1, 2].zip([3, 4])",
    "enumerate": "[1, 2].enumerate()",
}


@pytest.mark.parametrize("source", _VIEWS.values(), ids=_VIEWS.keys())
def test_a_lazy_view_is_a_set_element(
    source: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(f"{{{source}}}.len().print()")
    assert capsys.readouterr().out == "1\n"


@pytest.mark.parametrize("source", _VIEWS.values(), ids=_VIEWS.keys())
def test_a_lazy_view_equals_itself_and_no_other(
    source: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(
        f"v = {source}\n(v == v).print()\n(v == {source}).print()\n(v != v).print()"
    )
    assert capsys.readouterr().out == "True\nFalse\nFalse\n"
