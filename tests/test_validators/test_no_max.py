import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_max import NoMaxValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoMaxValidator().validate(tree)


def test_max_call_raises_validation_error() -> None:
    tree = ast.parse("max(a, b)")
    with pytest.raises(ValidationError) as exc_info:
        NoMaxValidator().validate(tree)
    assert "max()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("max(a, b)")
    with pytest.raises(ValidationError, match="a.max"):
        NoMaxValidator().validate(tree)


def test_max_carries_line_number() -> None:
    tree = ast.parse("x = 1\nmax(a, b)")
    with pytest.raises(ValidationError) as exc_info:
        NoMaxValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_max_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.max(other)")
    NoMaxValidator().validate(tree)
