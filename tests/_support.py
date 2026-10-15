"""Helpers the test modules import by name.

Kept out of `conftest.py`, which pytest loads for fixtures and discourages
importing from.
"""

import ast
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    import io

    from poop.transformers.base import Transformer

# The repository root, for the tests that read its files.
REPO_ROOT = Path(__file__).resolve().parents[1]

# The packages whose POOP-authored messages the static sweeps read.
SWEPT_PACKAGES = (REPO_ROOT / "poop" / "types", REPO_ROOT / "poop" / "transformers")

# The example corpus, discovered once: four modules walked `examples/` on
# their own, and a fifth was about to. A test parametrised over it names each
# case by `example_id`, the path under `examples/`.
EXAMPLES_DIR = REPO_ROOT / "examples"
EXAMPLE_FILES: tuple[Path, ...] = tuple(sorted(EXAMPLES_DIR.rglob("*.py")))


def example_id(path: Path) -> str:
    """`basics/hello_world.py` — the parametrize id for an example."""
    return str(path.relative_to(EXAMPLES_DIR))


def transform(transformer: Transformer, source: str) -> ast.Module:
    """`source` parsed and run through one transformer."""
    return transformer.transform(ast.parse(source))


def rewritten(transformer: Transformer, source: str) -> str:
    """`source` run through one transformer, unparsed back to source."""
    return ast.unparse(transform(transformer, source))


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
