import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_setattr import NoSetattrValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoSetattrValidator().validate(tree)


def test_setattr_raises_validation_error() -> None:
    tree = ast.parse("setattr(x, 'foo', 1)")
    with pytest.raises(ValidationError, match="setattr()"):
        NoSetattrValidator().validate(tree)


def test_delattr_raises_validation_error() -> None:
    tree = ast.parse("delattr(x, 'foo')")
    with pytest.raises(ValidationError, match="delattr()"):
        NoSetattrValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nsetattr(x, 'foo', 1)")
    with pytest.raises(ValidationError) as exc_info:
        NoSetattrValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_setattr_error_suggests_set_attr() -> None:
    tree = ast.parse("setattr(x, 'foo', 1)")
    with pytest.raises(ValidationError, match=r"set_attr"):
        NoSetattrValidator().validate(tree)


def test_delattr_error_suggests_del_attr() -> None:
    tree = ast.parse("delattr(x, 'foo')")
    with pytest.raises(ValidationError, match=r"del_attr"):
        NoSetattrValidator().validate(tree)
