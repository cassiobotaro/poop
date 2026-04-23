import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_assert import NoAssertValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAssertValidator().validate(tree)


def test_assert_raises_validation_error() -> None:
    tree = ast.parse("assert x > 0")
    with pytest.raises(ValidationError) as exc_info:
        NoAssertValidator().validate(tree)
    assert "assert" in str(exc_info.value)
    assert "assert_" in str(exc_info.value)


def test_assert_with_message_raises_validation_error() -> None:
    tree = ast.parse("assert x > 0, 'must be positive'")
    with pytest.raises(ValidationError):
        NoAssertValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    source = "x = 1\nassert x > 0"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoAssertValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_assert_inside_function_is_rejected() -> None:
    source = "def f():\n    assert True"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoAssertValidator().validate(tree)
