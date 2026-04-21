import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_chr import NoChrValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoChrValidator().validate(tree)


def test_chr_raises_validation_error() -> None:
    tree = ast.parse("chr(65)")
    with pytest.raises(ValidationError, match="chr()"):
        NoChrValidator().validate(tree)


def test_ord_raises_validation_error() -> None:
    tree = ast.parse("ord('A')")
    with pytest.raises(ValidationError, match="ord()"):
        NoChrValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("chr(65)")
    with pytest.raises(ValidationError, match="obj.chr"):
        NoChrValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nchr(65)")
    with pytest.raises(ValidationError) as exc_info:
        NoChrValidator().validate(tree)
    assert exc_info.value.lineno == 2
