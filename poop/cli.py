import ast
import json
import sys
from collections.abc import Generator
from contextlib import contextmanager
from importlib.metadata import version as _installed_version
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

import typer
from rich.syntax import Syntax

from poop.console import ERR, OUT, error_line, in_colour
from poop.errors import (
    ExecutionError,
    ParseError,
    PoopError,
    TransformError,
    ValidationError,
    report,
)
from poop.interpreter import Interpreter
from poop.repl import Repl

if TYPE_CHECKING:
    from rich.console import Console

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")

# One exit code per failure kind, so a script can branch on it. 1 is the
# unreadable file (`_unreadable`); 2 is shared with typer's usage errors on
# purpose — a parse error and a bad flag both say "this is not a program";
# a transform error is the interpreter failing while running the program,
# and exits as a run-time failure does.
UNREADABLE = 1
EXIT_CODES: dict[type[PoopError], int] = {
    ParseError: 2,
    ValidationError: 3,
    TransformError: 4,
    ExecutionError: 4,
}


def exit_code(exc: PoopError) -> int:
    return EXIT_CODES[type(exc)]


@contextmanager
def _poop_errors(source: str | None = None) -> Generator[None]:
    try:
        yield
    except PoopError as exc:
        report(exc, source, ERR)
        raise typer.Exit(exit_code(exc)) from exc


def _write(console: Console, text: str) -> None:
    """One line on `console`, as typed: no markup, no highlighting, no wrap.

    Every line the CLI writes goes through one of the two consoles, so the
    `NO_COLOR` / pipe decision is rich's for each stream — not rich's for the
    errors and click's for the line after them.
    """
    console.print(text, soft_wrap=True, highlight=False, markup=False)


def _unreadable(file: Path, reason: str | None) -> typer.Exit:
    """The exit for a source file that cannot be read, its cause already worded.

    An unreadable path (missing file, a directory, no permission) or a
    non-UTF-8 file is an ordinary user mistake; keep the one-line `poop:`
    style instead of leaking a rich-formatted traceback through typer.
    """
    error_line(ERR, f"poop: cannot read '{file}': {reason}")
    return typer.Exit(UNREADABLE)


def _stdin_is_a_terminal() -> bool:
    """Whether standard input is interactive — the REPL's one condition.

    A function rather than an inline `isatty` so a test can decide it:
    `CliRunner` hands the command a pipe for stdin, and the REPL test must
    still reach the REPL.
    """
    return sys.stdin.isatty()


def _read_stdin() -> str:
    """Standard input as a program, the byte-order mark spent as a file's is."""
    return sys.stdin.read().removeprefix("\ufeff")


def _source_from(file: Path | None, code: str | None) -> tuple[str, str] | None:
    """The program to run and its name, or `None` when the REPL is wanted.

    In this order: a path, `-` for standard input, `-c`, and a standard
    input that is not a terminal — which runs as a program, with no banner
    and no prompt, as `python3 < file` does. A program piped into `poop`
    used to get the REPL, whose banner and prompts landed on stdout between
    its own lines. Only an interactive stdin with nothing else to run is
    the REPL.
    """
    if file is not None and file != Path("-"):
        return _read_source(file), str(file)
    if file is not None:
        return _read_stdin(), "<stdin>"
    if code is not None:
        return code, "<string>"
    if not _stdin_is_a_terminal():
        return _read_stdin(), "<stdin>"
    return None


def _as_records(errors: list[ValidationError]) -> list[dict[str, object]]:
    return [
        {
            "line": err.lineno,
            "col": err.col_offset,
            "message": err.message,
            "validator": err.validator,
        }
        for err in errors
    ]


def _version(wanted: bool) -> None:
    if wanted:
        _write(OUT, f"poop {_installed_version('poop')}")
        raise typer.Exit


def _read_source(file: Path) -> str:
    try:
        # `utf-8-sig`, not `utf-8`: an editor's byte-order mark would otherwise
        # survive as a literal U+FEFF in the source and the tokenizer would
        # answer `invalid non-printable character U+FEFF` — about a character
        # invisible in every editor, from a file `python3` runs. CPython's own
        # loader strips it; the codec is identical to `utf-8` otherwise.
        return file.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise _unreadable(file, exc.strerror) from exc
    except UnicodeDecodeError as exc:
        # Not an OSError, and it words its cause as `reason`, not `strerror`.
        raise _unreadable(file, exc.reason) from exc


def _validators_only(
    interpreter: Interpreter, source: str, filename: str, output_format: str
) -> None:
    with _poop_errors(source):
        errors = interpreter.validate_all(source, filename)
    if output_format == "json":
        # Data on stdout, for an editor or CI: one object per error, in
        # source order, the validator named so a consumer can group or
        # silence by rule. `ensure_ascii=False` keeps the em-dash readable.
        _write(OUT, json.dumps(_as_records(errors), ensure_ascii=False))
    elif not errors:
        _write(OUT, "No validation errors.")
    else:
        for err in errors:
            report(err, source, ERR)
    if errors:
        raise typer.Exit(exit_code(errors[0]))


def _transformers_only(interpreter: Interpreter, source: str, filename: str) -> None:
    with _poop_errors(source):
        tree = interpreter.transform_source(source, filename)
    code = ast.unparse(tree)
    if in_colour(OUT):
        # `background_color="default"` keeps the terminal's own background
        # instead of painting a themed block behind the dump.
        OUT.print(Syntax(code, "python", theme="ansi_dark", background_color="default"))
    else:
        _write(OUT, code)


@app.command()
def main(  # noqa: PLR0913, PLR0917 — typer reads the command line off this signature
    file: Annotated[
        Path | None,
        typer.Argument(help="Source file to run, or - for standard input"),
    ] = None,
    code: Annotated[
        str | None, typer.Option("-c", help="Run this program instead of a file")
    ] = None,
    validators_only: Annotated[
        bool,
        typer.Option(
            "--validators-only", help="Run validators only, report all errors"
        ),
    ] = False,
    transformers_only: Annotated[
        bool,
        typer.Option(
            "--transformers-only", help="Run up to transformers and dump the AST"
        ),
    ] = False,
    output_format: Annotated[
        Literal["text", "json"],
        typer.Option(
            "--format", help="With --validators-only: the report as text or JSON"
        ),
    ] = "text",
    version: Annotated[  # noqa: ARG001 — consumed by its eager callback
        bool,
        typer.Option(
            "--version", callback=_version, is_eager=True, help="Print the version"
        ),
    ] = False,
) -> None:
    if validators_only and transformers_only:
        raise typer.BadParameter(
            "--validators-only and --transformers-only cannot be combined"
        )
    if output_format == "json" and not validators_only:
        raise typer.BadParameter("--format json needs --validators-only")
    interpreter = Interpreter()

    program = _source_from(file, code)
    if program is None:
        # A mode flag with nothing to run used to start the REPL in silence.
        for flag, wanted in (
            ("--validators-only", validators_only),
            ("--transformers-only", transformers_only),
        ):
            if wanted:
                raise typer.BadParameter(f"{flag} needs a file or piped input")
        Repl(interpreter).run()
        return
    source, filename = program

    if validators_only:
        _validators_only(interpreter, source, filename, output_format)
    elif transformers_only:
        _transformers_only(interpreter, source, filename)
    else:
        with _poop_errors(source):
            interpreter.run_source(source, filename)


def entry_point() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    entry_point()
