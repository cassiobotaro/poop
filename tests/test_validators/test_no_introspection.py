import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_introspection import NoIntrospectionValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIntrospectionValidator().validate(tree)


def test_globals_raises_validation_error() -> None:
    tree = ast.parse("globals()")
    with pytest.raises(ValidationError, match="globals()"):
        NoIntrospectionValidator().validate(tree)


def test_locals_raises_validation_error() -> None:
    tree = ast.parse("locals()")
    with pytest.raises(ValidationError, match="locals()"):
        NoIntrospectionValidator().validate(tree)


def test_vars_raises_validation_error() -> None:
    tree = ast.parse("vars(x)")
    with pytest.raises(ValidationError, match="vars()"):
        NoIntrospectionValidator().validate(tree)


def test_dir_raises_validation_error() -> None:
    tree = ast.parse("dir(x)")
    with pytest.raises(ValidationError, match="dir()"):
        NoIntrospectionValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nglobals()")
    with pytest.raises(ValidationError) as exc_info:
        NoIntrospectionValidator().validate(tree)
    assert exc_info.value.lineno == 2
