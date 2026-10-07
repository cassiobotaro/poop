"""Helpers the test modules import by name.

Kept out of `conftest.py`, which pytest loads for fixtures and discourages
importing from.
"""

import ast
from collections.abc import Callable
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    import io
    from pathlib import Path

    from poop.transformers.base import Transformer


def transform(transformer: Transformer, source: str) -> ast.Module:
    """`source` parsed and run through one transformer."""
    return transformer.transform(ast.parse(source))


# The `feed_input` fixture's type, for a test's signature.
type FeedInput = Callable[..., None]


def console(buf: io.StringIO, *, terminal: bool = True) -> Console:
    """A console writing to `buf`, as a colour terminal or as a pipe."""
    return Console(
        file=buf,
        force_terminal=terminal,
        color_system="standard",
        no_color=not terminal,
    )


# The `source_file` fixture's type: write a program, answer its path.
type SourceFile = Callable[..., Path]
