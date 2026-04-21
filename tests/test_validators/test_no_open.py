import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_open import NoOpenValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoOpenValidator().validate(tree)


def test_open_raises_validation_error() -> None:
    tree = ast.parse("open('file.txt')")
    with pytest.raises(ValidationError, match="open()"):
        NoOpenValidator().validate(tree)


def test_open_carries_line_number() -> None:
    tree = ast.parse("x = 1\nopen('file.txt')")
    with pytest.raises(ValidationError) as exc_info:
        NoOpenValidator().validate(tree)
    assert exc_info.value.lineno == 2
