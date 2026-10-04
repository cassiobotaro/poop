from typing import TYPE_CHECKING, ClassVar

from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

if TYPE_CHECKING:
    import ast

    from poop.errors import ValidationError


class _Visitor(ErrorCollector):
    def __init__(self, forbidden: frozenset[str], message: str) -> None:
        super().__init__()
        self._forbidden = forbidden
        self._message = message

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self._forbidden:
            self.report(self._message.format(name=node.id), node)
        self.generic_visit(node)


class CallNameValidator(CollectingValidator):
    """Forbids referencing a builtin by name.

    Rejects any reference to a forbidden name regardless of context —
    call (`len(xs)`), assignment (`f = len`), argument (`xs.map(len)`),
    decorator, or default — so the forbidden names are fully reserved
    identifiers and the wrapper layer cannot be reopened by aliasing.
    Method substitutes are unaffected: `xs.len()` / `n.hex()` are
    `ast.Attribute` nodes and keyword-argument names are not `Name` nodes.

    A subclass sets `forbidden` and `message`; `{name}` in the message is the
    name that was used.
    """

    # Read by the REPL's `:explain`, which derives its topic list from the
    # validators themselves. A name banned here but missing there gets
    # answered with "it may simply be allowed" — the opposite of the truth.
    forbidden: ClassVar[frozenset[str]]
    message: ClassVar[str]

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(self.forbidden, self.message), tree)
