from enum import IntEnum
from typing import ClassVar


class ExitCode(IntEnum):
    """The process exit code for each kind of failure, so a script can branch on it.

    Named for what the code tells a script. `NOT_A_PROGRAM` is shared with
    typer's usage errors on purpose: a parse error and a bad flag both say
    "this is not a program". A transform error is the interpreter failing while
    running the program, and exits `FAILED` as a run-time failure does.
    """

    UNREADABLE = 1
    NOT_A_PROGRAM = 2
    REFUSED = 3
    FAILED = 4


class PoopError(Exception):
    """Base for all interpreter errors.

    Declares the whole surface the renderers in `poop/report.py` read — a
    message and where it points — so `format_error` reads attributes instead
    of probing each subclass with `getattr`. `col_offset` is `ast`'s
    convention: 0-based, in UTF-8 bytes, which is what `_caret_column` there
    converts from.
    """

    # What the CLI exits with. `FAILED` on the base, so a class that declares no
    # code of its own still exits as a failure.
    exit_code: ClassVar[ExitCode] = ExitCode.FAILED
    lineno: int | None = None
    col_offset: int | None = None
    # The exception chain under a run-time failure, one sentence per link;
    # empty for every other kind of error.
    chain: tuple[str, ...] = ()

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

    exit_code = ExitCode.NOT_A_PROGRAM

    @classmethod
    def from_syntax_error(cls, exc: SyntaxError) -> ParseError:
        """The parser's failure, keeping the position CPython already found.

        `str(exc)` would flatten it into the text — `'(' was never closed
        (bad.py, line 2)` — and the error a newcomer hits first would lose the
        source line and caret every other error gets.

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

    exit_code = ExitCode.REFUSED

    # Narrower than `PoopError`'s `int | None` on purpose: a parse error may
    # have no position, but a validator always has a node, so this class
    # guarantees one. ty reads a narrowed writable attribute as unsound; here
    # it is the documented contract.
    lineno: int  # ty: ignore[incompatible-mutable-override]
    col_offset: int  # ty: ignore[incompatible-mutable-override]

    # The validator that refused, by module name (`no_print`) — the identifier
    # `--format json` hands an editor. Stamped by `collect_errors`, the one
    # place every validator's errors pass through; an error built by hand
    # has none.
    validator: str | None = None

    def __init__(self, message: str, lineno: int, col_offset: int) -> None:
        super().__init__(message, lineno, col_offset)


class TransformError(PoopError):
    """Raised when a transformer fails while rewriting the AST."""

    exit_code = ExitCode.FAILED

    def __init__(self, message: str, transformer: str) -> None:
        self.transformer = transformer
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} (transformer {self.transformer})"


class ExecutionError(PoopError):
    """Raised when exec() raises during evaluation."""

    exit_code = ExitCode.FAILED

    def __init__(
        self, message: str, lineno: int | None = None, chain: tuple[str, ...] = ()
    ) -> None:
        super().__init__(message, lineno)
        self.chain = chain
