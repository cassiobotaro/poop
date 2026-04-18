import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_if import NoIfValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIfValidator().validate(tree)


def test_if_statement_raises_validation_error() -> None:
    tree = ast.parse("if True:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoIfValidator().validate(tree)
    assert "if statements" in str(exc_info.value)


def test_if_expression_raises_validation_error() -> None:
    tree = ast.parse("x = 1 if True else 2")
    with pytest.raises(ValidationError) as exc_info:
        NoIfValidator().validate(tree)
    assert "ternary" in str(exc_info.value)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nif True:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoIfValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_if_inside_function_is_rejected() -> None:
    source = "def foo():\n    if True:\n        pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoIfValidator().validate(tree)


def test_error_message_mentions_polymorphism() -> None:
    tree = ast.parse("x = 1 if True else 2")
    with pytest.raises(ValidationError, match="polymorphism"):
        NoIfValidator().validate(tree)
