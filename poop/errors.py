import re


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


# Python's tokenizer ends a line only on \n, \r\n or \r, so those are the
# breaks the reported lineno counts. str.splitlines() also breaks on \v, \f,
# \x1c-\x1e, \x85, \u2028 and \u2029 — all legal inside a source file —
# which would number the lines differently from the parser and point at the
# wrong one.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")


def format_error(exc: PoopError, source: str | None) -> str:
    """Render an error, with the offending source line and a caret under it.

    Shared by the CLI and the REPL so one program reports the same way on both
    surfaces. The REPL used to print the bare message, citing a line and column
    that pointed into a buffer already scrolled away — while holding the source
    in hand.

    The position is stated once. With the source line in view, the gutter
    carries the line number and the caret the column, so the `(line N, col M)`
    suffix that `__str__` appends is dropped as repetition; with no line to
    point at, that suffix is the only clue and stays.
    """
    lineno = getattr(exc, "lineno", None)
    lines = _LINE_BREAK.split(source) if source is not None else []
    if lineno is None or not 1 <= lineno <= len(lines):
        return f"poop: {exc}"
    message = exc.args[0] if exc.args else str(exc)
    line = lines[lineno - 1]
    parts = [f"poop: {message}", f"  {lineno} | {line}"]
    col = getattr(exc, "col_offset", None)
    if col is not None:
        # ast reports col_offset as a UTF-8 *byte* offset while the gutter
        # prints characters, so a non-ASCII character earlier on the line
        # pushed the caret one column right per extra byte.
        caret_col = len(line.encode("utf-8")[:col].decode("utf-8", errors="replace"))
        caret_gutter = "  " + " " * len(str(lineno)) + " | "
        parts.append(f"{caret_gutter}{' ' * caret_col}^")
    return "\n".join(parts)
