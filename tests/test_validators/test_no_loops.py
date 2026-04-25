import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_loops import NoLoopsValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoLoopsValidator().validate(tree)


def test_for_loop_raises_validation_error() -> None:
    tree = ast.parse("for i in range(10):\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoLoopsValidator().validate(tree)
    assert "for loops" in str(exc_info.value)


def test_while_loop_raises_validation_error() -> None:
    tree = ast.parse("while True:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoLoopsValidator().validate(tree)
    assert "while loops" in str(exc_info.value)


def test_for_loop_carries_line_number() -> None:
    tree = ast.parse("x = 1\nfor i in range(10):\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoLoopsValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_while_loop_carries_line_number() -> None:
    tree = ast.parse("x = 1\nwhile True:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoLoopsValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_for_inside_function_is_rejected() -> None:
    source = "def foo():\n    for i in range(10):\n        pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoLoopsValidator().validate(tree)


def test_async_for_loop_raises_validation_error() -> None:
    source = "async def foo():\n    async for i in aiter():\n        pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoLoopsValidator().validate(tree)
    assert "async for loops" in str(exc_info.value)


def test_error_message_suggests_do_block() -> None:
    tree = ast.parse("for i in range(10):\n    pass")
    with pytest.raises(ValidationError, match="do"):
        NoLoopsValidator().validate(tree)
