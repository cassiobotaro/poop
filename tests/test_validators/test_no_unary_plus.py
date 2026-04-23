import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_unary_plus import NoUnaryPlusValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoUnaryPlusValidator().validate(tree)


def test_unary_minus_is_not_affected() -> None:
    tree = ast.parse("x = -1")
    NoUnaryPlusValidator().validate(tree)


def test_unary_plus_on_variable_raises() -> None:
    tree = ast.parse("x = 1\ny = +x")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryPlusValidator().validate(tree)
    assert "unary plus" in str(exc_info.value)


def test_unary_plus_on_literal_raises() -> None:
    tree = ast.parse("x = +1")
    with pytest.raises(ValidationError):
        NoUnaryPlusValidator().validate(tree)


def test_error_message_says_write_directly() -> None:
    tree = ast.parse("x = +1")
    with pytest.raises(ValidationError, match="directly"):
        NoUnaryPlusValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ny = +x")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryPlusValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_unary_plus_inside_lambda_is_rejected() -> None:
    tree = ast.parse("f = lambda x: +x")
    with pytest.raises(ValidationError):
        NoUnaryPlusValidator().validate(tree)
