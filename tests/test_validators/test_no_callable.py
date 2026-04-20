import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_callable import NoCallableValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoCallableValidator().validate(tree)


def test_callable_raises_validation_error() -> None:
    tree = ast.parse("callable(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoCallableValidator().validate(tree)
    assert "callable()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("callable(x)")
    with pytest.raises(ValidationError, match="obj.callable()"):
        NoCallableValidator().validate(tree)


def test_callable_carries_line_number() -> None:
    tree = ast.parse("x = 1\ncallable(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoCallableValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_callable_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.callable()")
    NoCallableValidator().validate(tree)
