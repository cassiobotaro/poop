"""Shared pytest fixtures for the POOP test suite.

Plain helpers that tests import by name live in `tests/_support.py`;
pytest discourages importing from a conftest.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

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


@pytest.fixture
def source_file(tmp_path: Path) -> SourceFile:
    """Write a POOP program under `tmp_path` as UTF-8 and answer its path."""

    def _write(text: str, name: str = "prog.py") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path

    return _write
