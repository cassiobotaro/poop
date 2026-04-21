import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_all import NoAllValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAllValidator().validate(tree)


def test_all_call_raises_validation_error() -> None:
    tree = ast.parse("all(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoAllValidator().validate(tree)
    assert "all()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("all(x)")
    with pytest.raises(ValidationError, match="col.all"):
        NoAllValidator().validate(tree)


def test_all_carries_line_number() -> None:
    tree = ast.parse("x = 1\nall(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoAllValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_all_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.all(lambda x: x)")
    NoAllValidator().validate(tree)
