import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_pow import NoPowValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoPowValidator().validate(tree)


def test_pow_raises_validation_error() -> None:
    tree = ast.parse("pow(2, 10)")
    with pytest.raises(ValidationError, match="pow()"):
        NoPowValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("pow(2, 10)")
    with pytest.raises(ValidationError, match="a.pow"):
        NoPowValidator().validate(tree)


def test_pow_carries_line_number() -> None:
    tree = ast.parse("x = 1\npow(2, 10)")
    with pytest.raises(ValidationError) as exc_info:
        NoPowValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_pow_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.pow(10)")
    NoPowValidator().validate(tree)
