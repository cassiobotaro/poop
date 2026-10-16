"""Shared pytest fixtures for the POOP test suite.

Plain helpers that tests import by name live in `tests/_support.py`;
pytest discourages importing from a conftest.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from poop.repl import Repl
    from tests._support import FeedInput, SourceFile


@pytest.fixture
def feed_input(monkeypatch: pytest.MonkeyPatch) -> FeedInput:
    """Answer `input()` with `responses`, raising any that is an exception.

    `EOFError()` ends a REPL session the way Ctrl-D does, and
    `KeyboardInterrupt()` the way Ctrl-C does.
    """

    def _feed(*responses: str | BaseException) -> None:
        answers = iter(responses)

        def _input(_prompt: str = "") -> str:
            answer = next(answers)
            if isinstance(answer, BaseException):
                raise answer
            return answer

        monkeypatch.setattr("builtins.input", _input)

    return _feed


# Named through `name=`: a module-level function called `repl` would rebind
# the `poop.repl` module a test file imports under that name.
@pytest.fixture(name="repl")
def _repl(tmp_path: Path) -> Repl:
    """A REPL whose history lives under `tmp_path`, not in the developer's home."""
    from poop.interpreter import Interpreter  # noqa: PLC0415 — a fixture's own import
    from poop.repl import Repl  # noqa: PLC0415

    return Repl(Interpreter(), history=tmp_path / "history")


@pytest.fixture
def source_file(tmp_path: Path) -> SourceFile:
    """Write a POOP program under `tmp_path` as UTF-8 and answer its path."""

    def _write(text: str, name: str = "prog.py") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path

    return _write
