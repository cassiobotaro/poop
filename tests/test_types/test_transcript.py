import pytest

from poop.types.transcript import transcript


def test_show_prints_string(capsys: pytest.CaptureFixture[str]) -> None:
    transcript.show("hello")
    assert capsys.readouterr().out == "hello\n"


def test_show_converts_to_str(capsys: pytest.CaptureFixture[str]) -> None:
    transcript.show(42)
    assert capsys.readouterr().out == "42\n"


def test_nl_prints_empty_line(capsys: pytest.CaptureFixture[str]) -> None:
    transcript.nl()
    assert capsys.readouterr().out == "\n"


def test_transcript_is_singleton() -> None:
    from poop.types.transcript import transcript as t2

    assert transcript is t2


def test_show_returns_self(capsys: pytest.CaptureFixture[str]) -> None:
    assert transcript.show("x") is transcript


def test_nl_returns_self(capsys: pytest.CaptureFixture[str]) -> None:
    assert transcript.nl() is transcript


def test_show_cascade(capsys: pytest.CaptureFixture[str]) -> None:
    transcript.show("hello").nl().show("world")
    assert capsys.readouterr().out == "hello\n\nworld\n"
