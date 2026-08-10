"""Counts the docs state are the counts the code has.

Three numbers had drifted at once — `CLAUDE.md` said 69 validators, `README.md`
said ~69 and 41 example programs, against 70 and 43 — and every one of them is
derivable. A test asserting `len(DEFAULT_VALIDATORS) == 70` would only move the
problem to a fourth place to keep in step; this reads the numbers *out of the
Markdown* and compares them against the live registries, so the prose cannot
fall behind without failing.

The same argument `test_no_python_wording.py`'s static half makes for messages
nobody remembered to write a program for.
"""

import pathlib
import re

import pytest

from poop.validators import DEFAULT_VALIDATORS

_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _validator_count() -> int:
    return len(DEFAULT_VALIDATORS)


def _example_count() -> int:
    return len(list((_ROOT / "examples").rglob("*.py")))


# (file, pattern capturing one number, what the number must equal). The
# patterns are deliberately narrow: a sentence rewrite that drops the number
# fails the "found it at all" test below rather than passing vacuously.
_CLAIMS: tuple[tuple[str, str, str], ...] = (
    ("CLAUDE.md", r"`print`, (\d+) in all", "validators"),
    ("README.md", r"POOP runs (\d+) validators on every program", "validators"),
    ("README.md", r"ships (\d+) programs across three subfolders", "examples"),
)

_ACTUAL = {"validators": _validator_count, "examples": _example_count}


@pytest.mark.parametrize(
    ("filename", "pattern", "kind"),
    _CLAIMS,
    ids=[f"{name}-{kind}" for name, _, kind in _CLAIMS],
)
def test_a_documented_count_matches_the_code(
    filename: str, pattern: str, kind: str
) -> None:
    text = (_ROOT / filename).read_text(encoding="utf-8")
    match = re.search(pattern, text)
    assert match is not None, (
        f"{filename} no longer states its {kind} count in the expected shape "
        f"({pattern!r}) — update the pattern or restore the sentence"
    )
    assert int(match.group(1)) == _ACTUAL[kind](), (
        f"{filename} says {match.group(1)} {kind}, the code has {_ACTUAL[kind]()}"
    )


def test_the_readme_lists_every_example_it_ships() -> None:
    """The prose count and the bullet list below it must agree too.

    The list was right while the sentence above it was two behind, which is
    what made the drift invisible to a reader skimming either one.
    """
    text = (_ROOT / "README.md").read_text(encoding="utf-8")
    listed = re.findall(r"^- \[`([a-z0-9_]+\.py)`\]", text, flags=re.MULTILINE)
    on_disk = {path.name for path in (_ROOT / "examples").rglob("*.py")}
    assert set(listed) == on_disk
    assert len(listed) == len(on_disk), "an example is listed twice"
