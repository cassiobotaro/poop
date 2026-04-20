import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_walrus import NoWalrusValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoWalrusValidator().validate(tree)


def test_walrus_raises_validation_error() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        x = (y := 1)")
    with pytest.raises(ValidationError) as exc_info:
        NoWalrusValidator().validate(tree)
    assert ":=" in str(exc_info.value)


def test_walrus_carries_line_number() -> None:
    tree = ast.parse("x = 1\nclass Foo:\n    def m(self):\n        x = (y := 1)")
    with pytest.raises(ValidationError) as exc_info:
        NoWalrusValidator().validate(tree)
    assert exc_info.value.lineno == 4
