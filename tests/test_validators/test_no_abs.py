import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_abs import NoAbsValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAbsValidator().validate(tree)


def test_abs_call_raises_validation_error() -> None:
    tree = ast.parse("abs(-1)")
    with pytest.raises(ValidationError) as exc_info:
        NoAbsValidator().validate(tree)
    assert "abs()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("abs(-1)")
    with pytest.raises(ValidationError, match="obj.abs()"):
        NoAbsValidator().validate(tree)


def test_abs_inside_method_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        abs(self)")
    with pytest.raises(ValidationError):
        NoAbsValidator().validate(tree)


def test_abs_carries_line_number() -> None:
    tree = ast.parse("x = 1\nabs(-1)")
    with pytest.raises(ValidationError) as exc_info:
        NoAbsValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_abs_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.abs()")
    NoAbsValidator().validate(tree)
