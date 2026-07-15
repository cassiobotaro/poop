import ast
from collections.abc import Iterable

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector


def make_call_name_validator(
    *,
    forbidden: Iterable[str],
    message: str,
) -> type:
    """Factory for validators that forbid referencing a builtin by name.

    Rejects any reference to a forbidden name regardless of context —
    call (`len(xs)`), assignment (`f = len`), argument (`xs.map(len)`),
    decorator, or default — so the forbidden names are fully reserved
    identifiers and the wrapper layer cannot be reopened by aliasing.
    Method substitutes are unaffected: `xs.len()` / `n.hex()` are
    `ast.Attribute` nodes and keyword-argument names are not `Name` nodes.

    Args:
        forbidden: Builtin names to forbid (e.g., {"len", "abs"})
        message: Error message template with {name} placeholder

    Returns:
        A Validator class that forbids any reference to the given names.
    """
    names = frozenset(forbidden)

    class _Visitor(ErrorCollector):
        def visit_Name(self, node: ast.Name) -> None:
            if node.id in names:
                self.report(message.format(name=node.id), node)
            self.generic_visit(node)

    class _Validator(CollectingValidator):
        # Exposed so the REPL's `:explain` can derive its topic list from the
        # validators themselves. A name banned here but missing there gets
        # answered with "it may simply be allowed" — the opposite of the truth.
        forbidden = names

        def collect(self, tree: ast.Module) -> list[ValidationError]:
            visitor = _Visitor()
            visitor.visit(tree)
            return visitor.errors

    return _Validator
