import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_and_or import NoAndOrValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAndOrValidator().validate(tree)


def test_not_is_not_affected() -> None:
    tree = ast.parse("x = True\ny = not x")
    NoAndOrValidator().validate(tree)


def test_and_raises_validation_error() -> None:
    tree = ast.parse("x = True and False")
    with pytest.raises(ValidationError) as exc_info:
        NoAndOrValidator().validate(tree)
    assert "and operator" in str(exc_info.value)


def test_and_error_message_mentions_and_method() -> None:
    tree = ast.parse("x = True and False")
    with pytest.raises(ValidationError, match=r"\.and_\("):
        NoAndOrValidator().validate(tree)


def test_or_raises_validation_error() -> None:
    tree = ast.parse("x = True or False")
    with pytest.raises(ValidationError) as exc_info:
        NoAndOrValidator().validate(tree)
    assert "or operator" in str(exc_info.value)


def test_or_error_message_mentions_or_method() -> None:
    tree = ast.parse("x = True or False")
    with pytest.raises(ValidationError, match=r"\.or_\("):
        NoAndOrValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ny = True and False")
    with pytest.raises(ValidationError) as exc_info:
        NoAndOrValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_and_inside_lambda_is_rejected() -> None:
    tree = ast.parse("f = lambda: True and False")
    with pytest.raises(ValidationError):
        NoAndOrValidator().validate(tree)


def test_nested_or_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return True or False"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoAndOrValidator().validate(tree)
