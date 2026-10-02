import ast
from typing import Any, ClassVar, Protocol

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

    A subclass names its `visitor`, as a transformer names its `rewriter`, and
    `collect` walks the tree with a fresh one. A visitor that needs arguments
    overrides `collect` instead. One of the two is checked when the subclass
    is defined, so a validator that forgot both fails at import rather than on
    the first program it is handed.
    """

    visitor: ClassVar[type[ErrorCollector]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.collect is CollectingValidator.collect and not hasattr(cls, "visitor"):
            raise TypeError(
                f"{cls.__name__} sets no `visitor` and overrides no `collect`"
            )

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(self.visitor(), tree)

    def validate(self, tree: ast.Module) -> None:
        errors = self.collect(tree)
        if errors:
            raise errors[0]


def iter_params(args: ast.arguments) -> list[ast.arg]:
    """Every parameter an `ast.arguments` binds, `*args`/`**kwargs` included.

    Positional, positional-only and keyword-only parameters plus the vararg
    and kwarg, in a single flat list. A parameter binds a name inside the body
    exactly like an assignment does, so validators guarding names (reserved
    prefixes, namespace shadows) need to inspect all of them.
    """
    params = [*args.posonlyargs, *args.args, *args.kwonlyargs]
    if args.vararg is not None:
        params.append(args.vararg)
    if args.kwarg is not None:
        params.append(args.kwarg)
    return params


def collect_errors(visitor: ErrorCollector, tree: ast.Module) -> list[ValidationError]:
    """Run `visitor` over `tree` and hand back what it recorded.

    Every `collect` implementation is the same three-step dance — build the
    visitor, walk the tree, read `errors` back off it. Naming it once keeps the
    visitor contract (rejections land in `.errors`) in a single place.
    """
    visitor.visit(tree)
    return visitor.errors
