import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_raise import NoRaiseValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoRaiseValidator().validate(tree)


def test_raise_statement_raises_validation_error() -> None:
    source = "raise ValueError('oops')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoRaiseValidator().validate(tree)
    assert "raise" in str(exc_info.value)


def test_raise_without_argument_raises_validation_error() -> None:
    source = "raise"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoRaiseValidator().validate(tree)


def test_error_message_suggests_substitute() -> None:
    source = "raise KeyError('missing')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="raise_"):
        NoRaiseValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    source = "x = 1\nraise ValueError('oops')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoRaiseValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_raise_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        raise RuntimeError('err')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoRaiseValidator().validate(tree)
