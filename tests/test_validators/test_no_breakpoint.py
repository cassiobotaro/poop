import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_breakpoint import NoBreakpointValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoBreakpointValidator().validate(tree)


def test_breakpoint_raises_validation_error() -> None:
    tree = ast.parse("breakpoint()")
    with pytest.raises(ValidationError, match="breakpoint()"):
        NoBreakpointValidator().validate(tree)


def test_breakpoint_carries_line_number() -> None:
    tree = ast.parse("x = 1\nbreakpoint()")
    with pytest.raises(ValidationError) as exc_info:
        NoBreakpointValidator().validate(tree)
    assert exc_info.value.lineno == 2
