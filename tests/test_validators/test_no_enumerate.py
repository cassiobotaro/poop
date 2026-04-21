import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_enumerate import NoEnumerateValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoEnumerateValidator().validate(tree)


def test_enumerate_raises_validation_error() -> None:
    tree = ast.parse("enumerate(x)")
    with pytest.raises(ValidationError, match="enumerate()"):
        NoEnumerateValidator().validate(tree)


def test_zip_raises_validation_error() -> None:
    tree = ast.parse("zip(a, b)")
    with pytest.raises(ValidationError, match="zip()"):
        NoEnumerateValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nenumerate(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoEnumerateValidator().validate(tree)
    assert exc_info.value.lineno == 2
