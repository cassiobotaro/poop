import ast
from collections.abc import Iterable

from poop.errors import ValidationError


def make_call_name_validator(
    *,
    forbidden: Iterable[str],
    message: str,
) -> type:
    """Factory for validators that forbid calling functions by name.

    Args:
        forbidden: Function names to forbid (e.g., {"len", "abs"})
        message: Error message template with {name} placeholder

    Returns:
        A Validator class that forbids calls to the given names.
    """
    names = frozenset(forbidden)

    class _Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id in names:
                raise ValidationError(
                    message.format(name=node.func.id),
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            self.generic_visit(node)

    class _Validator:
        def validate(self, tree: ast.Module) -> None:
            _Visitor().visit(tree)

    return _Validator
