from operator import attrgetter
from typing import TYPE_CHECKING

from poop.errors import TransformError, ValidationError
from poop.executor import execute
from poop.parser import parse
from poop.transformers import DEFAULT_NAMESPACE, DEFAULT_TRANSFORMERS
from poop.validators import DEFAULT_VALIDATORS

if TYPE_CHECKING:
    import ast

    from poop.transformers import Transformer
    from poop.validators import Validator


class Interpreter:
    def __init__(
        self,
        validators: list[Validator] | None = None,
        transformers: list[Transformer] | None = None,
        namespace: dict[str, object] | None = None,
    ) -> None:
        # Copies, not the lists themselves: `validators` hands its list out, and
        # handing out `DEFAULT_VALIDATORS` let one interpreter's `append` rewrite
        # the registry of every interpreter built after it, the REPL's included.
        self._validators: list[Validator] = list(
            validators if validators is not None else DEFAULT_VALIDATORS
        )
        self._transformers: list[Transformer] = list(
            transformers if transformers is not None else DEFAULT_TRANSFORMERS
        )
        self._namespace: dict[str, object] = (
            namespace if namespace is not None else DEFAULT_NAMESPACE
        )

    @property
    def validators(self) -> list[Validator]:
        return self._validators

    def new_namespace(self) -> dict[str, object]:
        """A fresh copy of the namespace programs run against."""
        return dict(self._namespace)

    def run_source(self, source: str, filename: str = "<string>") -> None:
        tree = self.transform_source(source, filename)
        execute(tree, filename=filename, namespace=self.new_namespace())

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
        return sorted(
            (
                error
                for validator in self._validators
                for error in validator.collect(tree)
            ),
            key=attrgetter("lineno", "col_offset"),
        )

    def run_source_repl(
        self, source: str, namespace: dict[str, object], filename: str = "<repl>"
    ) -> None:
        # Each REPL input needs its own filename: a traceback carries frames
        # from functions defined in *earlier* inputs too, and their line
        # numbers count against that earlier buffer. A per-input filename lets
        # the executor keep only frames from the input being run, so a reported
        # line always exists in the source shown alongside it.
        tree = self.transform_source(source, filename=filename)
        execute(tree, filename=filename, namespace=namespace, interactive=True)

    def transform_source(self, source: str, filename: str = "<string>") -> ast.Module:
        tree: ast.Module = parse(source, filename=filename)
        for validator in self._validators:
            validator.validate(tree)
        for transformer in self._transformers:
            try:
                tree = transformer.transform(tree)
            except Exception as exc:
                raise TransformError(str(exc), type(transformer).__name__) from exc
        return tree
