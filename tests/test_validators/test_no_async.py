import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_async import NoAsyncValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("class Foo:\n    def bar(self):\n        return 1")
    NoAsyncValidator().validate(tree)


def test_async_method_passes() -> None:
    tree = ast.parse("class Foo:\n    async def bar(self):\n        return 1")
    NoAsyncValidator().validate(tree)


def test_free_async_function_is_left_to_no_free_functions() -> None:
    NoAsyncValidator().validate(ast.parse("async def foo():\n    return 1"))


def test_await_in_an_async_method_names_its_substitute() -> None:
    tree = ast.parse("class Foo:\n    async def bar(self):\n        await self.x()")
    with pytest.raises(ValidationError) as exc_info:
        NoAsyncValidator().validate(tree)
    assert exc_info.value.message == "await is forbidden — use x.await_() instead"
    assert exc_info.value.lineno == 3


def test_module_level_await_raises() -> None:
    # ast.parse accepts a module-level await — only compile() rejects it.
    # Without its own row the node would reach compile() and surface as a
    # raw CPython SyntaxError rather than a POOP error.
    tree = ast.parse("await foo()")
    with pytest.raises(ValidationError, match="await is forbidden"):
        NoAsyncValidator().validate(tree)


def test_async_with_and_for_are_left_to_their_own_validators() -> None:
    # ast.parse accepts these at module level too, so they are real nodes
    # a validator must catch — but no_with and no_loops already own them,
    # and duplicating the rows here would just double the error.
    NoAsyncValidator().validate(ast.parse("async with lock:\n    pass"))
    NoAsyncValidator().validate(ast.parse("async for x in y:\n    pass"))
