import ast
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.repl import Repl

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")


@contextmanager
def _poop_errors() -> Iterator[None]:
    try:
        yield
    except PoopError as exc:
        typer.echo(f"poop: {exc}", err=True)
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

    source = file.read_text(encoding="utf-8")
    filename = str(file)

    if validators_only:
        with _poop_errors():
            errors = interpreter.validate_all(source, filename)
        if not errors:
            typer.echo("No validation errors.")
            return
        for err in errors:
            typer.echo(str(err), err=True)
        raise typer.Exit(1)

    if transformers_only:
        with _poop_errors():
            tree = interpreter.transform_source(source, filename)
        typer.echo(ast.unparse(tree))
        return

    with _poop_errors():
        interpreter.run_file(file)


def entry_point() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    entry_point()
