import ast
from pathlib import Path

from poop.executor import execute
from poop.parser import parse
from poop.validators import DEFAULT_VALIDATORS, Validator


class Interpreter:
    def __init__(self, validators: list[Validator] | None = None) -> None:
        self._validators: list[Validator] = (
            validators if validators is not None else DEFAULT_VALIDATORS
        )

    def run_file(self, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        self.run_source(source, filename=str(path))

    def run_source(self, source: str, filename: str = "<string>") -> None:
        tree: ast.Module = parse(source, filename=filename)
        for validator in self._validators:
            validator.validate(tree)
        execute(tree, filename=filename)
