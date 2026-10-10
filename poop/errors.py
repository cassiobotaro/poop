import re
import unicodedata
from itertools import starmap
from typing import TYPE_CHECKING

from rich.syntax import Syntax
from rich.text import Text

from poop.console import in_colour

if TYPE_CHECKING:
    from rich.console import Console


class PoopError(Exception):
    """Base for all interpreter errors.

    Declares the whole surface the renderers read — a message and where it
    points — so `format_error` reads attributes instead of probing each
    subclass with `getattr`. `col_offset` is `ast`'s convention: 0-based, in
    UTF-8 bytes, which is what `_caret_column` converts from.
    """

    lineno: int | None = None
    col_offset: int | None = None

    def __init__(
        self, message: str, lineno: int | None = None, col_offset: int | None = None
    ) -> None:
        self.lineno = lineno
        self.col_offset = col_offset
        super().__init__(message)

    @property
    def message(self) -> str:
        """The sentence alone, without the location `__str__` appends."""
        return self.args[0]

    def __str__(self) -> str:
        where = [
            f"{label} {value}"
            for label, value in (("line", self.lineno), ("col", self.col_offset))
            if value is not None
        ]
        return f"{self.message} ({', '.join(where)})" if where else self.message


class ParseError(PoopError):
    """Raised when the source is not Python at all."""

    @classmethod
    def from_syntax_error(cls, exc: SyntaxError) -> ParseError:
        """The parser's failure, keeping the position CPython already found.

        `str(exc)` flattened it into the text — `'(' was never closed (bad.py,
        line 2)` — so the one error a newcomer hits first was the one reported
        without the source line and caret every other error gets.

        `SyntaxError.offset` counts *characters* from 1; `col_offset` is
        `ast`'s 0-based UTF-8 byte offset, so `x = "éé" +* 2` is 11 to one and
        12 to the other. Converted here, once, against the line CPython quotes.
        """
        col = None
        if exc.offset is not None and exc.text is not None:
            col = len(exc.text[: max(exc.offset - 1, 0)].encode("utf-8"))
        return cls(exc.msg, exc.lineno, col)


class ValidationError(PoopError):
    """Raised when a validator rejects the AST."""

    lineno: int
    col_offset: int

    def __init__(self, message: str, lineno: int, col_offset: int) -> None:
        super().__init__(message, lineno, col_offset)


class TransformError(PoopError):
    """Raised when a transformer fails while rewriting the AST."""

    def __init__(self, message: str, transformer: str) -> None:
        self.transformer = transformer
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} (transformer {self.transformer})"


class ExecutionError(PoopError):
    """Raised when exec() raises during evaluation."""

    def __init__(self, message: str, lineno: int | None = None) -> None:
        super().__init__(message, lineno)


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
    lineno = exc.lineno
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


def _column_width(char: str) -> int:
    """The columns one character takes: a combining mark none, a wide one two."""
    if unicodedata.combining(char):
        return 0
    if unicodedata.east_asian_width(char) in {"W", "F"}:
        return 2
    return 1


def _display_width(text: str) -> int:
    """How many terminal columns `text` occupies.

    The third conversion in the same family as the two below, and the same
    argument: a tab is one character wide to `len` and eight to the reader, and
    a CJK ideograph is one character wide to `len` and **two**. `len` measured
    the first correctly only because `_quoted` had already expanded it.

    Wide and full-width characters count two, combining marks count zero — the
    two cases Unicode gives a stable answer for. A decomposed `á` is `a` plus
    U+0301: legal Python source, visually identical to the precomposed form,
    and two characters to `len`, so the caret used to run *past* its target
    there while it fell short on CJK and emoji.

    Grapheme clusters are where this stops, deliberately. A ZWJ emoji family is
    seven code points and one column, flag sequences are two and two, and
    terminals disagree about several of them; `unicodedata` has no answer and a
    `wcwidth` dependency is not a trade worth making for a caret.
    """
    return sum(map(_column_width, text))


def _caret_column(line: str, col: int) -> int:
    # Three conversions, in this order. ast reports col_offset as a UTF-8 *byte*
    # offset while the gutter prints characters, so a non-ASCII character
    # earlier on the line pushed the caret one column right per extra byte;
    # then the prefix is expanded like the quoted line, since a tab is one
    # character wide to `len` and eight to the reader; then it is measured in
    # the columns a terminal actually spends on it, since the caret line is
    # spaces — one column each — and the quoted line is not.
    prefix = line.encode("utf-8")[:col].decode("utf-8", errors="replace")
    return _display_width(_quoted(prefix))


def _line_gutter(lineno: int) -> str:
    """The `  N | ` prefix that precedes the quoted source line."""
    return f"  {lineno} | "


def _caret_gutter(lineno: int) -> str:
    """The blank-numbered gutter aligning the caret under the source line."""
    return "  " + " " * len(str(lineno)) + " | "


# The style `render_error` reads as "syntax-highlight this segment" rather
# than as a rich style name.
_CODE = "code"


def _error_segments(exc: PoopError, source: str | None) -> list[tuple[str, str]]:
    """The error's layout once, as `(text, style)` pairs.

    `poop:` and the message, the numbered gutter quoting the offending line,
    and a caret under the column. `format_error` keeps the texts and
    `render_error` the styles; the layout used to be written in both, by hand.

    The position is stated once. With the source line in view, the gutter
    carries the line number and the caret the column, so the `(line N, col M)`
    suffix that `__str__` appends is dropped as repetition; with no line to
    point at, that suffix is the only clue and stays.
    """
    location = _error_location(exc, source)
    if location is None:
        return [(f"poop: {exc}", "red")]
    lineno, line = location
    segments = [
        (f"poop: {exc.message}\n", "red"),
        (_line_gutter(lineno), "dim"),
        (_quoted(line), _CODE),
    ]
    if exc.col_offset is not None:
        segments += [
            (f"\n{_caret_gutter(lineno)}", "dim"),
            (" " * _caret_column(line, exc.col_offset) + "^", "red"),
        ]
    return segments


def format_error(exc: PoopError, source: str | None) -> str:
    """Render an error, with the offending source line and a caret under it.

    Shared by the CLI and the REPL so one program reports the same way on both
    surfaces. The REPL used to print the bare message, citing a line and column
    that pointed into a buffer already scrolled away — while holding the source
    in hand. This is the plain-text form; `render_error` is the coloured,
    syntax-highlighted form a terminal gets.
    """
    return "".join(text for text, _ in _error_segments(exc, source))


def _styled(text: str, style: str) -> Text:
    if style != _CODE:
        return Text(text, style=style)
    highlighted = _PY_SYNTAX.highlight(text)
    highlighted.rstrip()  # the highlighter appends a trailing newline
    return highlighted


def render_error(exc: PoopError, source: str | None) -> Text:
    """Coloured, syntax-highlighted form of `format_error` for a terminal.

    Same segments — the message is red, the gutter dim, and the quoted line is
    Python-highlighted. Callers use it only when the destination console has
    colour; elsewhere `format_error`'s plain string is printed instead, so
    pipes and `NO_COLOR` are unaffected.
    """
    return Text.assemble(*starmap(_styled, _error_segments(exc, source)))


def report(exc: PoopError, source: str | None, console: Console) -> None:
    """Print `exc` on `console` the way both front ends do.

    A colour terminal gets the syntax-highlighted `render_error`; a pipe or
    `NO_COLOR` gets `format_error`'s plain text, with rich's markup and
    highlighting off so a `[` in the source is printed rather than parsed.
    The CLI and the REPL each carried this choice, one through `typer.echo`
    and one through the console, and only the rendering was shared.
    """
    if in_colour(console):
        console.print(render_error(exc, source), soft_wrap=True)
    else:
        console.print(
            format_error(exc, source), soft_wrap=True, highlight=False, markup=False
        )
