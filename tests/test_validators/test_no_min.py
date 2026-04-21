import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_min import NoMinValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoMinValidator().validate(tree)


def test_min_call_raises_validation_error() -> None:
    tree = ast.parse("min(a, b)")
    with pytest.raises(ValidationError) as exc_info:
        NoMinValidator().validate(tree)
    assert "min()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("min(a, b)")
    with pytest.raises(ValidationError, match="a.min"):
        NoMinValidator().validate(tree)


def test_min_carries_line_number() -> None:
    tree = ast.parse("x = 1\nmin(a, b)")
    with pytest.raises(ValidationError) as exc_info:
        NoMinValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_min_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.min(other)")
    NoMinValidator().validate(tree)
