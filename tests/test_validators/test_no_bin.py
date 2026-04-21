import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_bin import NoBinValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoBinValidator().validate(tree)


def test_bin_raises_validation_error() -> None:
    tree = ast.parse("bin(10)")
    with pytest.raises(ValidationError, match="bin()"):
        NoBinValidator().validate(tree)


def test_hex_raises_validation_error() -> None:
    tree = ast.parse("hex(255)")
    with pytest.raises(ValidationError, match="hex()"):
        NoBinValidator().validate(tree)


def test_oct_raises_validation_error() -> None:
    tree = ast.parse("oct(8)")
    with pytest.raises(ValidationError, match="oct()"):
        NoBinValidator().validate(tree)


def test_error_suggests_method() -> None:
    tree = ast.parse("bin(10)")
    with pytest.raises(ValidationError, match="n.bin"):
        NoBinValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nbin(10)")
    with pytest.raises(ValidationError) as exc_info:
        NoBinValidator().validate(tree)
    assert exc_info.value.lineno == 2
