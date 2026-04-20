import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_yield import NoYieldValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoYieldValidator().validate(tree)


def test_yield_raises_validation_error() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        yield 1")
    with pytest.raises(ValidationError) as exc_info:
        NoYieldValidator().validate(tree)
    assert "yield" in str(exc_info.value)


def test_yield_from_raises_validation_error() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        yield from [1, 2]")
    with pytest.raises(ValidationError) as exc_info:
        NoYieldValidator().validate(tree)
    assert "yield from" in str(exc_info.value)


def test_yield_carries_line_number() -> None:
    tree = ast.parse("x = 1\nclass Foo:\n    def m(self):\n        yield 1")
    with pytest.raises(ValidationError) as exc_info:
        NoYieldValidator().validate(tree)
    assert exc_info.value.lineno == 4
