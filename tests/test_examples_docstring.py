"""Every example opens with the Smalltalk it translates.

The corpus is the language's prose: each program's docstring names the
Smalltalk idiom it renders, under a `Smalltalk:` header — three qualify it in
parentheses (`Smalltalk (class-side cached instance):`), which the test admits
by prefix. Nothing checked the header, so a new example could ship without
the one line that says what it is for.
"""

import ast
from typing import TYPE_CHECKING

import pytest

from tests._support import EXAMPLE_FILES, example_id

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("example", EXAMPLE_FILES, ids=example_id)
def test_the_docstring_carries_a_smalltalk_header(example: Path) -> None:
    docstring = ast.get_docstring(ast.parse(example.read_text(encoding="utf-8")))
    assert docstring is not None, f"{example_id(example)} has no docstring"
    headers = [
        line
        for line in docstring.splitlines()
        if line.startswith("Smalltalk") and line.endswith(":")
    ]
    assert headers, f"{example_id(example)} names no `Smalltalk:` header"
