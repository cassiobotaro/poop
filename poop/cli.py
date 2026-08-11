import ast
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.syntax import Syntax

from poop.errors import PoopError, format_error, render_error
from poop.interpreter import Interpreter
from poop.repl import Repl

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")

# stdout for the AST dump, stderr for diagnostics — each detects its own tty and
# NO_COLOR, so `poop file 2>err.log` colours neither the redirected file nor a
# non-terminal, matching how the REPL renders on both streams.
_OUT = Console()
_ERR = Console(stderr=True)


def _emit_error(exc: PoopError, source: str | None) -> None:
    """Report a PoopError on stderr the same way the REPL does.

    A colour terminal gets the syntax-highlighted `render_error`; a pipe or
    NO_COLOR gets the plain `format_error` string, echoed through typer so it
    reaches the same stream typer would have used.
    """
    if _ERR.is_terminal and not _ERR.no_color:
        _ERR.print(render_error(exc, source), soft_wrap=True)
    else:
        typer.echo(format_error(exc, source), err=True)


@contextmanager
def _poop_errors(source: str | None = None) -> Iterator[None]:
    try:
        yield
    except PoopError as exc:
        _emit_error(exc, source)
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
    interpreter = Interpreter()

    if file is None:
        Repl(interpreter).run()
        return

    try:
        # `utf-8-sig`, not `utf-8`: an editor's byte-order mark would otherwise
        # survive as a literal U+FEFF in the source and the tokenizer would
        # answer `invalid non-printable character U+FEFF` — about a character
        # invisible in every editor, from a file `python3` runs. CPython's own
        # loader strips it; the codec is identical to `utf-8` otherwise.
        source = file.read_text(encoding="utf-8-sig")
    except OSError as exc:
        # An unreadable path (missing file, a directory, no permission) is
        # an ordinary user mistake; keep the one-line `poop:` style instead
        # of leaking a rich-formatted traceback through typer.
        typer.echo(f"poop: cannot read '{file}': {exc.strerror}", err=True)
        raise typer.Exit(1) from exc
    except UnicodeDecodeError as exc:
        # A non-UTF-8 source file is an ordinary user mistake too, but it is
        # not an OSError; keep the clean `poop:` style instead of leaking a
        # rich-formatted traceback through typer.
        typer.echo(f"poop: cannot read '{file}': {exc.reason}", err=True)
        raise typer.Exit(1) from exc
    filename = str(file)

    if validators_only:
        with _poop_errors(source):
            errors = interpreter.validate_all(source, filename)
        if not errors:
            typer.echo("No validation errors.")
            return
        for err in errors:
            _emit_error(err, source)
        raise typer.Exit(1)

    if transformers_only:
        with _poop_errors(source):
            tree = interpreter.transform_source(source, filename)
        code = ast.unparse(tree)
        if _OUT.is_terminal and not _OUT.no_color:
            # `background_color="default"` keeps the terminal's own background
            # instead of painting a themed block behind the dump.
            _OUT.print(
                Syntax(code, "python", theme="ansi_dark", background_color="default")
            )
        else:
            typer.echo(code)
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
