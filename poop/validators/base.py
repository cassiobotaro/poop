import ast
from typing import Protocol

from poop.errors import ValidationError


class Validator(Protocol):
    def validate(self, tree: ast.Module) -> None: ...

    def collect(self, tree: ast.Module) -> list[ValidationError]: ...


class ErrorCollector(ast.NodeVisitor):
    """NodeVisitor that records rejections instead of raising them.

    Raising aborts the walk at the first hit — right for running a program,
    wrong for `--validators-only`, whose help promises to report all errors:
    three `if`s used to answer exactly one.
    """

    def __init__(self) -> None:
        self.errors: list[ValidationError] = []

    def report(self, message: str, node: ast.AST) -> None:
        self.errors.append(
            ValidationError(
                message,
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )
        )


class CollectingValidator:
    """Derives `validate` from `collect` — one traversal, two contracts.

    Running a program wants the first error and stops; `--validators-only`
    wants every occurrence. Collecting is the primitive because the reverse
    cannot be built: a raise has already thrown away the rest of the walk.
    """

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        raise NotImplementedError

    def validate(self, tree: ast.Module) -> None:
        errors = self.collect(tree)
        if errors:
            raise errors[0]


def collect_errors(visitor: ErrorCollector, tree: ast.Module) -> list[ValidationError]:
    """Run `visitor` over `tree` and hand back what it recorded.

    Every `collect` implementation is the same three-step dance — build the
    visitor, walk the tree, read `errors` back off it. Naming it once keeps the
    visitor contract (rejections land in `.errors`) in a single place.
    """
    visitor.visit(tree)
    return visitor.errors
