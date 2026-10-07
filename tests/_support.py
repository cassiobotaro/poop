"""Helpers the test modules import by name.

Kept out of `conftest.py`, which pytest loads for fixtures and discourages
importing from.
"""

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poop.transformers.base import Transformer


def transform(transformer: Transformer, source: str) -> ast.Module:
    """`source` parsed and run through one transformer."""
    return transformer.transform(ast.parse(source))
