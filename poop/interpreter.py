import ast
from pathlib import Path
from typing import TYPE_CHECKING

from poop.errors import TransformError, ValidationError
from poop.executor import execute
from poop.parser import parse
from poop.transformers import DEFAULT_NAMESPACE, DEFAULT_TRANSFORMERS
from poop.validators import DEFAULT_VALIDATORS

if TYPE_CHECKING:
    from poop.transformers import Transformer
    from poop.validators import Validator


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
        tree = self._validate_and_transform(source, filename)
        execute(tree, filename=filename, namespace=dict(self._namespace))

    def validate_all(
        self, source: str, filename: str = "<string>"
    ) -> list[ValidationError]:
        """Every rejection in the file, in source order.

        `validate` stops at the first error per validator, which reported one
        `if` out of three and emitted in DEFAULT_VALIDATORS order — so errors
        on lines 2, 3, 4, 5 came back as 3, 5, 2, 4. Collecting reports every
        occurrence; sorting puts them in the order they are read in.
        """
        tree: ast.Module = parse(source, filename=filename)
        errors: list[ValidationError] = [
            error for validator in self._validators for error in validator.collect(tree)
        ]
        errors.sort(key=lambda error: (error.lineno, error.col_offset))
        return errors

    def transform_source(self, source: str, filename: str = "<string>") -> ast.Module:
        return self._validate_and_transform(source, filename)

    def run_source_repl(
        self, source: str, namespace: dict[str, object], filename: str = "<repl>"
    ) -> None:
        # Each REPL input needs its own filename: a traceback carries frames
        # from functions defined in *earlier* inputs too, and their line
        # numbers count against that earlier buffer. A per-input filename lets
        # the executor keep only frames from the input being run, so a reported
        # line always exists in the source shown alongside it.
        tree = self._validate_and_transform(source, filename=filename)
        execute(tree, filename=filename, namespace=namespace, interactive=True)

    def _validate_and_transform(self, source: str, filename: str) -> ast.Module:
        tree: ast.Module = parse(source, filename=filename)
        for validator in self._validators:
            validator.validate(tree)
        for transformer in self._transformers:
            try:
                tree = transformer.transform(tree)
            except Exception as exc:
                raise TransformError(str(exc), type(transformer).__name__) from exc
        return tree
