import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_match import NoMatchValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoMatchValidator().validate(tree)


def test_match_raises_validation_error() -> None:
    tree = ast.parse(
        "class Foo:\n    def m(self, x):\n        match x:\n            case 1:\n                pass"
    )
    with pytest.raises(ValidationError) as exc_info:
        NoMatchValidator().validate(tree)
    assert "match" in str(exc_info.value)


def test_error_mentions_polymorphism() -> None:
    tree = ast.parse(
        "class Foo:\n    def m(self, x):\n        match x:\n            case 1:\n                pass"
    )
    with pytest.raises(ValidationError, match="polymorphism"):
        NoMatchValidator().validate(tree)


def test_match_carries_line_number() -> None:
    tree = ast.parse(
        "x = 1\nclass Foo:\n    def m(self, x):\n        match x:\n            case 1:\n                pass"
    )
    with pytest.raises(ValidationError) as exc_info:
        NoMatchValidator().validate(tree)
    assert exc_info.value.lineno == 4
