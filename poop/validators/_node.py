import ast
from collections.abc import Callable, Mapping

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors


def make_node_validator(
    messages: Mapping[type[ast.AST], str],
) -> type[CollectingValidator]:
    """Factory for validators that forbid specific AST node types.

    Args:
        messages: Mapping from AST node type to error message. One
            visit_<NodeType> method is generated per entry.

    Returns:
        A Validator class that reports every banned node.
    """

    def _make_visit(msg: str) -> Callable[[ErrorCollector, ast.AST], None]:
        def visit(self: ErrorCollector, node: ast.AST) -> None:
            self.report(msg, node)
            # Descend into the rejected node rather than stopping there: an
            # `if` nested in an `if` is two rewrites, and reporting only the
            # outer one restores the fix-one/rerun loop this exists to end.
            self.generic_visit(node)

        return visit

    visitor_methods: dict[str, object] = {
        f"visit_{node_type.__name__}": _make_visit(msg)
        for node_type, msg in messages.items()
    }
    visitor_cls = type("_Visitor", (ErrorCollector,), visitor_methods)

    class _Validator(CollectingValidator):
        def collect(self, tree: ast.Module) -> list[ValidationError]:
            return collect_errors(visitor_cls(), tree)

    return _Validator
