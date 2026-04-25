import ast
from pathlib import Path

from poop.executor import execute
from poop.parser import parse
from poop.transformers import DEFAULT_NAMESPACE, DEFAULT_TRANSFORMERS, Transformer
from poop.validators import DEFAULT_VALIDATORS, Validator


class Interpreter:
    def __init__(
        self,
        validators: list[Validator] | None = None,
        transformers: list[Transformer] | None = None,
        namespace: dict[str, object] | None = None,
    ) -> None:
        self._validators: list[Validator] = (
            validators if validators is not None else DEFAULT_VALIDATORS
        )
        self._transformers: list[Transformer] = (
            transformers if transformers is not None else DEFAULT_TRANSFORMERS
        )
        self._namespace: dict[str, object] = (
            namespace if namespace is not None else DEFAULT_NAMESPACE
        )

    def run_file(self, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        self.run_source(source, filename=str(path))

    def run_source(self, source: str, filename: str = "<string>") -> None:
        tree: ast.Module = parse(source, filename=filename)
        for validator in self._validators:
            validator.validate(tree)
        for transformer in self._transformers:
            tree = transformer.transform(tree)
        execute(tree, filename=filename, namespace=dict(self._namespace))

    def run_source_repl(self, source: str, namespace: dict[str, object]) -> None:
        tree: ast.Module = parse(source, filename="<repl>")
        for validator in self._validators:
            validator.validate(tree)
        for transformer in self._transformers:
            tree = transformer.transform(tree)
        execute(tree, filename="<repl>", namespace=namespace)
