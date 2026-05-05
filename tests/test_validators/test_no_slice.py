import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_slice import NoSliceValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoSliceValidator().validate(tree)


def test_slice_raises_validation_error() -> None:
    tree = ast.parse("slice(1, 10)")
    with pytest.raises(ValidationError, match="slice()"):
        NoSliceValidator().validate(tree)


def test_error_suggests_slice_method() -> None:
    tree = ast.parse("slice(1, 10)")
    with pytest.raises(ValidationError, match=r"obj\.slice"):
        NoSliceValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nslice(1, 10)")
    with pytest.raises(ValidationError) as exc_info:
        NoSliceValidator().validate(tree)
    assert exc_info.value.lineno == 2
