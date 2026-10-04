import ast

import pytest

from poop.errors import ParseError
from poop.parser import parse


def test_parse_valid_source_returns_module() -> None:
    result = parse("x = 1 + 2")
    assert isinstance(result, ast.Module)


def test_parse_syntax_error_raises_parse_error() -> None:
    with pytest.raises(ParseError):
        parse("def :")


def test_parse_error_carries_the_position() -> None:
    # Kept as attributes, not flattened into the text, so the error renders
    # with the source line and a caret like every other one.
    with pytest.raises(ParseError) as exc_info:
        parse("x = 1\ny = (2 +\nz = 3\n")
    assert exc_info.value.message == "'(' was never closed"
    assert (exc_info.value.lineno, exc_info.value.col_offset) == (2, 4)


def test_a_syntax_error_without_a_quoted_line_carries_no_column() -> None:
    # CPython leaves `text` empty for some failures; with no line to measure
    # against, there is no byte offset to give, and the caret is left out.
    error = ParseError.from_syntax_error(SyntaxError("bad", ("f", 3, 2, None)))
    assert (error.lineno, error.col_offset) == (3, None)


def test_parse_error_column_is_in_utf8_bytes() -> None:
    # CPython's offset counts characters from 1; the caret code reads `ast`'s
    # 0-based byte offset. Two two-byte characters put the two 1 apart.
    with pytest.raises(ParseError) as exc_info:
        parse('x = "\u00e9\u00e9" +* 2\n')
    assert exc_info.value.col_offset == 12
