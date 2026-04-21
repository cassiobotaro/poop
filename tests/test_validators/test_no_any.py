import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_any import NoAnyValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAnyValidator().validate(tree)


def test_any_call_raises_validation_error() -> None:
    tree = ast.parse("any(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoAnyValidator().validate(tree)
    assert "any()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("any(x)")
    with pytest.raises(ValidationError, match="col.any"):
        NoAnyValidator().validate(tree)


def test_any_carries_line_number() -> None:
    tree = ast.parse("x = 1\nany(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoAnyValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_any_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.any(lambda x: x)")
    NoAnyValidator().validate(tree)
