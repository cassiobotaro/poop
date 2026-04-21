import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_hasattr import NoHasattrValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoHasattrValidator().validate(tree)


def test_hasattr_raises_validation_error() -> None:
    tree = ast.parse("hasattr(x, 'foo')")
    with pytest.raises(ValidationError, match="hasattr()"):
        NoHasattrValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("hasattr(x, 'foo')")
    with pytest.raises(ValidationError, match="has_attr"):
        NoHasattrValidator().validate(tree)


def test_hasattr_carries_line_number() -> None:
    tree = ast.parse("x = 1\nhasattr(x, 'foo')")
    with pytest.raises(ValidationError) as exc_info:
        NoHasattrValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_has_attr_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.has_attr('foo')")
    NoHasattrValidator().validate(tree)
