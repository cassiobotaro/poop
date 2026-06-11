import ast
from collections.abc import Iterable

from poop.errors import ValidationError


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

    class _Visitor(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name) -> None:
            if node.id in names:
                raise ValidationError(
                    message.format(name=node.id),
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            self.generic_visit(node)

    class _Validator:
        def validate(self, tree: ast.Module) -> None:
            _Visitor().visit(tree)

    return _Validator
