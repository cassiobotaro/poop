import ast
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.syntax import Syntax

from poop.console import ERR, OUT, in_colour
from poop.errors import PoopError, report
from poop.interpreter import Interpreter
from poop.repl import Repl

if TYPE_CHECKING:
    from rich.console import Console

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")


@contextmanager
def _poop_errors(source: str | None = None) -> Iterator[None]:
    try:
        yield
    except PoopError as exc:
        report(exc, source, ERR)
        raise typer.Exit(1) from exc


def _write(console: Console, text: str) -> None:
    """One line on `console`, as typed: no markup, no highlighting, no wrap.

    Every line the CLI writes goes through one of the two consoles, so the
    `NO_COLOR` / pipe decision is rich's for each stream — not rich's for the
    errors and click's for the line after them.
    """
    console.print(text, soft_wrap=True, highlight=False, markup=False)


def _read_source(file: Path) -> str:
    try:
        # `utf-8-sig`, not `utf-8`: an editor's byte-order mark would otherwise
        # survive as a literal U+FEFF in the source and the tokenizer would
        # answer `invalid non-printable character U+FEFF` — about a character
        # invisible in every editor, from a file `python3` runs. CPython's own
        # loader strips it; the codec is identical to `utf-8` otherwise.
        return file.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        # An unreadable path (missing file, a directory, no permission) or a
        # non-UTF-8 file is an ordinary user mistake; keep the one-line
        # `poop:` style instead of leaking a rich-formatted traceback through
        # typer. A decode error is not an OSError, and words its cause as
        # `reason` rather than `strerror`.
        reason = exc.strerror if isinstance(exc, OSError) else exc.reason
        _write(ERR, f"poop: cannot read '{file}': {reason}")
        raise typer.Exit(1) from exc


@app.command()
def main(
    file: Annotated[Path | None, typer.Argument(help="Source file to run")] = None,
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
) -> None:
    if validators_only and transformers_only:
        raise typer.BadParameter(
            "--validators-only and --transformers-only cannot be combined"
        )
    interpreter = Interpreter()

    if file is None:
        Repl(interpreter).run()
        return

    source = _read_source(file)
    filename = str(file)

    if validators_only:
        with _poop_errors(source):
            errors = interpreter.validate_all(source, filename)
        if not errors:
            _write(OUT, "No validation errors.")
            return
        for err in errors:
            report(err, source, ERR)
        raise typer.Exit(1)

    if transformers_only:
        with _poop_errors(source):
            tree = interpreter.transform_source(source, filename)
        code = ast.unparse(tree)
        if in_colour(OUT):
            # `background_color="default"` keeps the terminal's own background
            # instead of painting a themed block behind the dump.
            OUT.print(
                Syntax(code, "python", theme="ansi_dark", background_color="default")
            )
        else:
            _write(OUT, code)
        return

    with _poop_errors(source):
        # Execute the source already read above — do not re-read `file`.
        # A second read of a pipe (`poop /dev/stdin`) yields nothing, silently
        # running an empty program; it also lets the executed source drift from
        # the one the error gutter points at if the file changes between reads.
        interpreter.run_source(source, filename)


def entry_point() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    entry_point()
