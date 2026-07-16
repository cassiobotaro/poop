import ast
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from poop.errors import PoopError, format_error
from poop.interpreter import Interpreter
from poop.repl import Repl

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")


@contextmanager
def _poop_errors(source: str | None = None) -> Iterator[None]:
    try:
        yield
    except PoopError as exc:
        typer.echo(format_error(exc, source), err=True)
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
        source = file.read_text(encoding="utf-8")
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
            typer.echo(format_error(err, source), err=True)
        raise typer.Exit(1)

    if transformers_only:
        with _poop_errors(source):
            tree = interpreter.transform_source(source, filename)
        typer.echo(ast.unparse(tree))
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
