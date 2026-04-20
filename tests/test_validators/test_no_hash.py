import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_hash import NoHashValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoHashValidator().validate(tree)


def test_hash_call_raises_validation_error() -> None:
    tree = ast.parse("hash(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoHashValidator().validate(tree)
    assert "hash()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("hash(x)")
    with pytest.raises(ValidationError, match="obj.hash()"):
        NoHashValidator().validate(tree)


def test_hash_carries_line_number() -> None:
    tree = ast.parse("x = 1\nhash(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoHashValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_hash_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.hash()")
    NoHashValidator().validate(tree)
