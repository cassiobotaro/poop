import ast

from poop.errors import ParseError


def parse(source: str, filename: str = "<unknown>") -> ast.Module:
    try:
        return ast.parse(source, filename=filename, mode="exec")
    except SyntaxError as exc:
        raise ParseError(str(exc)) from exc
