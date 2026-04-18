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


def test_parse_filename_propagates() -> None:
    with pytest.raises(ParseError, match="myfile.py"):
        parse("def :", filename="myfile.py")
