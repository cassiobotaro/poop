import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_round import NoRoundValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoRoundValidator().validate(tree)


def test_round_call_raises_validation_error() -> None:
    tree = ast.parse("round(3.14)")
    with pytest.raises(ValidationError) as exc_info:
        NoRoundValidator().validate(tree)
    assert "round()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("round(3.14)")
    with pytest.raises(ValidationError, match="obj.round()"):
        NoRoundValidator().validate(tree)


def test_round_with_ndigits_raises() -> None:
    tree = ast.parse("round(3.14, 1)")
    with pytest.raises(ValidationError):
        NoRoundValidator().validate(tree)


def test_round_carries_line_number() -> None:
    tree = ast.parse("x = 1\nround(3.14)")
    with pytest.raises(ValidationError) as exc_info:
        NoRoundValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_round_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.round(2)")
    NoRoundValidator().validate(tree)
