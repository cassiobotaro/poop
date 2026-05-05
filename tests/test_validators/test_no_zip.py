import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_zip import NoZipValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoZipValidator().validate(tree)


def test_enumerate_is_now_allowed() -> None:
    tree = ast.parse("enumerate(x)")
    NoZipValidator().validate(tree)  # must not raise


def test_zip_raises_validation_error() -> None:
    tree = ast.parse("zip(a, b)")
    with pytest.raises(ValidationError, match="zip()"):
        NoZipValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nzip(a, b)")
    with pytest.raises(ValidationError) as exc_info:
        NoZipValidator().validate(tree)
    assert exc_info.value.lineno == 2
