"""An `async def` in a class body, awaited: the transformers treat it as a `def`."""

import asyncio

from poop.executor import execute
from poop.interpreter import Interpreter

_PROGRAM = """
class P:
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


def _p() -> object:
    interpreter = Interpreter()
    namespace = interpreter.new_namespace()
    execute(interpreter.transform_source(_PROGRAM), namespace=namespace)
    return namespace["P"]()


def _await(method: str, *args: object, **kwargs: object) -> object:
    return asyncio.run(getattr(_p(), method)(*args, **kwargs))


def test_falling_off_the_end_answers_none() -> None:
    assert _await("falls_off").is_none()


def test_a_bare_return_answers_none() -> None:
    assert _await("bare").is_none()


def test_variadic_positionals_are_a_poop_tuple() -> None:
    assert str(_await("count", 1, 2)) == "2"


def test_variadic_keywords_are_a_poop_dict() -> None:
    assert str(_await("keys", a=1)) == "1"


def test_a_docstring_stays_a_docstring() -> None:
    method = type(_p()).__dict__["documented"]
    assert method.__func__.__doc__ == "the docstring"
