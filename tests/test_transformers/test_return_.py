from functools import partial

import pytest

from poop.interpreter import Interpreter
from poop.transformers.return_ import ReturnTransformer
from tests._support import rewritten

_rewritten = partial(rewritten, ReturnTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def f():\n    x = 1", "def f():\n    x = 1\n    return _poop_none"),
        ("def f():\n    return", "def f():\n    return _poop_none"),
        # No trailing return is appended after an explicit one.
        ("def f():\n    return 5", "def f():\n    return 5"),
        # No trailing `return _poop_none` (would make __init__ return non-None).
        (
            "class C:\n    def __init__(self):\n        self.x = 1",
            "class C:\n\n    def __init__(self):\n        self.x = 1",
        ),
    ],
    ids=[
        "falloff_appends_poop_none_return",
        "bare_return_becomes_poop_none",
        "explicit_return_value_untouched",
        "init_is_skipped",
    ],
)
def test_return_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


def test_void_method_answers_none_via_interpreter() -> None:
    Interpreter().run_source(
        "class Greeter:\n"
        "    def greet(self):\n"
        "        'hi'.print()\n"
        "Greeter().greet().is_none().print()"
    )


def test_init_still_constructs_via_interpreter() -> None:
    Interpreter().run_source(
        "class Box:\n"
        "    def __init__(self, v):\n"
        "        self._v = v\n"
        "    def value(self):\n"
        "        return self._v\n"
        "Box(7).value().print()"
    )
