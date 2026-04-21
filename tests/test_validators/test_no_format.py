import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_format import NoFormatValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoFormatValidator().validate(tree)


def test_format_raises_validation_error() -> None:
    tree = ast.parse("format(x, '.2f')")
    with pytest.raises(ValidationError, match="format()"):
        NoFormatValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("format(x, '.2f')")
    with pytest.raises(ValidationError, match="obj.format"):
        NoFormatValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nformat(x, '.2f')")
    with pytest.raises(ValidationError) as exc_info:
        NoFormatValidator().validate(tree)
    assert exc_info.value.lineno == 2
