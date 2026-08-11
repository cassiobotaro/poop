import re

from rich.syntax import Syntax
from rich.text import Text


class PoopError(Exception):
    """Base for all interpreter errors."""


class ParseError(PoopError):
    """Raised when ast.parse fails on source code."""


class ValidationError(PoopError):
    """Raised when a validator rejects the AST."""

    def __init__(self, message: str, lineno: int, col_offset: int) -> None:
        self.lineno = lineno
        self.col_offset = col_offset
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()} (line {self.lineno}, col {self.col_offset})"


class TransformError(PoopError):
    """Raised when a transformer fails while rewriting the AST."""

    def __init__(self, message: str, transformer: str) -> None:
        self.transformer = transformer
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()} (transformer {self.transformer})"


class ExecutionError(PoopError):
    """Raised when exec() raises during evaluation."""

    def __init__(self, message: str, lineno: int | None = None) -> None:
        self.lineno = lineno
        super().__init__(message)

    def __str__(self) -> str:
        if self.lineno is None:
            return super().__str__()
        return f"{super().__str__()} (line {self.lineno})"


# Python's tokenizer ends a line only on \n, \r\n or \r, so those are the breaks
# the reported lineno counts. str.splitlines() also breaks on \v, \f, \x1c-\x1e,
# \x85, U+2028 and U+2029 — all legal inside a source file — which would number
# the lines differently from the parser and point at the wrong one.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")

# One reusable highlighter for the single offending source line. `ansi_dark`
# maps onto the terminal's own 16-colour palette rather than a fixed truecolor
# theme, so the caret line adapts to the user's scheme; the console decides
# whether any of it is emitted, so a pipe still gets plain text.
_PY_SYNTAX = Syntax("", "python", theme="ansi_dark")


def _error_location(exc: PoopError, source: str | None) -> tuple[int, str] | None:
    """The line number and its source text, or None when neither is available.

    Returns None when the exception carries no line, when there is no source to
    quote, or when the line falls outside it — the cases where a caller can only
    show the bare message.
    """
    lineno = getattr(exc, "lineno", None)
    lines = _LINE_BREAK.split(source) if source is not None else []
    if lineno is None or not 1 <= lineno <= len(lines):
        return None
    return lineno, lines[lineno - 1]


def _quoted(line: str) -> str:
    """The source line as it is printed, with tabs already expanded.

    A tab is one character and eight columns, so quoting it raw put the caret
    in the indentation of every tab-indented file — and the terminal expanded
    those tabs from the start of the *printed* line, which begins with the
    gutter, so its stops did not even land where the file's do. Expanding here
    leaves no tab for the terminal to interpret; `_caret_column` measures the
    same expansion, so the two cannot disagree.
    """
    return line.expandtabs()


def _caret_column(line: str, col: int) -> int:
    # Two conversions, in this order. ast reports col_offset as a UTF-8 *byte*
    # offset while the gutter prints characters, so a non-ASCII character
    # earlier on the line pushed the caret one column right per extra byte;
    # then the prefix is expanded like the quoted line, since a tab is one
    # character wide to `len` and eight to the reader.
    prefix = line.encode("utf-8")[:col].decode("utf-8", errors="replace")
    return len(_quoted(prefix))


def _message(exc: PoopError) -> str:
    return exc.args[0] if exc.args else str(exc)


def _line_gutter(lineno: int) -> str:
    """The `  N | ` prefix that precedes the quoted source line."""
    return f"  {lineno} | "


def _caret_gutter(lineno: int) -> str:
    """The blank-numbered gutter aligning the caret under the source line."""
    return "  " + " " * len(str(lineno)) + " | "


def format_error(exc: PoopError, source: str | None) -> str:
    """Render an error, with the offending source line and a caret under it.

    Shared by the CLI and the REPL so one program reports the same way on both
    surfaces. The REPL used to print the bare message, citing a line and column
    that pointed into a buffer already scrolled away — while holding the source
    in hand. This is the plain-text form; `render_error` is the coloured,
    syntax-highlighted form a terminal gets.

    The position is stated once. With the source line in view, the gutter
    carries the line number and the caret the column, so the `(line N, col M)`
    suffix that `__str__` appends is dropped as repetition; with no line to
    point at, that suffix is the only clue and stays.
    """
    location = _error_location(exc, source)
    if location is None:
        return f"poop: {exc}"
    lineno, line = location
    parts = [f"poop: {_message(exc)}", f"{_line_gutter(lineno)}{_quoted(line)}"]
    col = getattr(exc, "col_offset", None)
    if col is not None:
        parts.append(f"{_caret_gutter(lineno)}{' ' * _caret_column(line, col)}^")
    return "\n".join(parts)


def render_error(exc: PoopError, source: str | None) -> Text:
    """Coloured, syntax-highlighted twin of `format_error` for a terminal.

    Same layout — `poop:` message, source gutter, caret — but the message is
    red, the gutter dim, and the quoted line is Python-highlighted. Callers use
    it only when the destination console has colour; elsewhere `format_error`'s
    plain string is printed instead, so pipes and `NO_COLOR` are unaffected.
    """
    location = _error_location(exc, source)
    if location is None:
        return Text(f"poop: {exc}", style="red")
    lineno, line = location
    highlighted = _PY_SYNTAX.highlight(_quoted(line))
    highlighted.rstrip()  # the highlighter appends a trailing newline
    rendered = Text.assemble(
        (f"poop: {_message(exc)}\n", "red"),
        (_line_gutter(lineno), "dim"),
        highlighted,
    )
    col = getattr(exc, "col_offset", None)
    if col is not None:
        rendered.append(f"\n{_caret_gutter(lineno)}", style="dim")
        rendered.append(f"{' ' * _caret_column(line, col)}^", style="red")
    return rendered
