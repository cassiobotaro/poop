import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_iter import NoIterValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIterValidator().validate(tree)


def test_iter_raises_validation_error() -> None:
    tree = ast.parse("iter(x)")
    with pytest.raises(ValidationError, match="iter()"):
        NoIterValidator().validate(tree)


def test_next_raises_validation_error() -> None:
    tree = ast.parse("next(x)")
    with pytest.raises(ValidationError, match="next()"):
        NoIterValidator().validate(tree)


def test_error_suggests_do() -> None:
    tree = ast.parse("iter(x)")
    with pytest.raises(ValidationError, match="do"):
        NoIterValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\niter(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoIterValidator().validate(tree)
    assert exc_info.value.lineno == 2
