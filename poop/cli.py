import ast
from pathlib import Path
from typing import Annotated, Optional

import typer

from poop.errors import PoopError

app = typer.Typer(name="poop", help="Python interpreter infected by Smalltalk")


@app.command()
def main(
    file: Annotated[Optional[Path], typer.Argument(help="Source file to run")] = None,
    validators_only: Annotated[
        bool,
        typer.Option("--validators-only", help="Run validators only, report all errors"),
    ] = False,
    transformers_only: Annotated[
        bool,
        typer.Option("--transformers-only", help="Run up to transformers and dump the AST"),
    ] = False,
    explain: Annotated[
        bool,
        typer.Option("--explain", help="Report all validation errors with substitute hints"),
    ] = False,
) -> None:
    from poop.interpreter import Interpreter

    interpreter = Interpreter()

    if file is None:
        from poop.repl import Repl

        Repl(interpreter).run()
        return

    source = file.read_text(encoding="utf-8")
    filename = str(file)

    if validators_only or explain:
        errors = interpreter.validate_all(source, filename)
        if not errors:
            typer.echo("No validation errors.")
            return
        for err in errors:
            typer.echo(str(err), err=True)
        raise typer.Exit(1)

    if transformers_only:
        try:
            tree = interpreter.transform_source(source, filename)
        except PoopError as exc:
            typer.echo(f"poop: {exc}", err=True)
            raise typer.Exit(1)
        typer.echo(ast.unparse(tree))
        return

    try:
        interpreter.run_file(file)
    except PoopError as exc:
        typer.echo(f"poop: {exc}", err=True)
        raise typer.Exit(1)


def entry_point() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    entry_point()
