import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_global import NoGlobalValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoGlobalValidator().validate(tree)


def test_global_raises_validation_error() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        global x")
    with pytest.raises(ValidationError, match="global"):
        NoGlobalValidator().validate(tree)


def test_nonlocal_raises_validation_error() -> None:
    tree = ast.parse(
        "class Foo:\n    def m(self):\n        def inner():\n            nonlocal x"
    )
    with pytest.raises(ValidationError, match="nonlocal"):
        NoGlobalValidator().validate(tree)


def test_global_carries_line_number() -> None:
    tree = ast.parse("x = 1\nclass Foo:\n    def m(self):\n        global x")
    with pytest.raises(ValidationError) as exc_info:
        NoGlobalValidator().validate(tree)
    assert exc_info.value.lineno == 4
