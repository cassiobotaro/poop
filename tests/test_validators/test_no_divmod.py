import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_divmod import NoDivmodValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoDivmodValidator().validate(tree)


def test_divmod_raises_validation_error() -> None:
    tree = ast.parse("divmod(10, 3)")
    with pytest.raises(ValidationError, match="divmod()"):
        NoDivmodValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("divmod(10, 3)")
    with pytest.raises(ValidationError, match="a.divmod"):
        NoDivmodValidator().validate(tree)


def test_divmod_carries_line_number() -> None:
    tree = ast.parse("x = 1\ndivmod(10, 3)")
    with pytest.raises(ValidationError) as exc_info:
        NoDivmodValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_divmod_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.divmod(3)")
    NoDivmodValidator().validate(tree)
