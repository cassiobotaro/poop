import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_isinstance import NoIsinstanceValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIsinstanceValidator().validate(tree)


def test_isinstance_call_raises_validation_error() -> None:
    tree = ast.parse("isinstance(x, int)")
    with pytest.raises(ValidationError) as exc_info:
        NoIsinstanceValidator().validate(tree)
    assert "isinstance()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("isinstance(x, int)")
    with pytest.raises(ValidationError, match="is_kind_of"):
        NoIsinstanceValidator().validate(tree)


def test_isinstance_carries_line_number() -> None:
    tree = ast.parse("x = 1\nisinstance(x, int)")
    with pytest.raises(ValidationError) as exc_info:
        NoIsinstanceValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_isinstance_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.is_kind_of(int)")
    NoIsinstanceValidator().validate(tree)
