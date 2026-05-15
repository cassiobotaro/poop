"""Shared pytest fixtures for the POOP test suite.

These helpers exist to keep the ~60 validator tests and ~25 transformer
tests focused on what's being tested rather than the boilerplate of
`ast.parse + pytest.raises(ValidationError)`. Existing tests continue
to work unchanged; new or refactored tests can opt in.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from poop.errors import ValidationError

if TYPE_CHECKING:
    from poop.validators.base import Validator


@pytest.fixture
def parse() -> Callable[[str], ast.Module]:
    return ast.parse


@pytest.fixture
def assert_rejects() -> Callable[..., ValidationError]:
    def _assert_rejects(
        validator: Validator,
        source: str,
        *,
        lineno: int | None = None,
        match: str | re.Pattern[str] | None = None,
    ) -> ValidationError:
        tree = ast.parse(source)
        with pytest.raises(ValidationError, match=match) as exc_info:
            validator.validate(tree)
        if lineno is not None:
            assert exc_info.value.lineno == lineno, (
                f"expected lineno={lineno}, got {exc_info.value.lineno}"
            )
        return exc_info.value

    return _assert_rejects
