import ast
from collections.abc import Callable, Mapping

from poop.errors import ValidationError


def make_node_validator(messages: Mapping[type[ast.AST], str]) -> type:
    """Factory for validators that forbid specific AST node types.

    Args:
        messages: Mapping from AST node type to error message. One
            visit_<NodeType> method is generated per entry.

    Returns:
        A Validator class that raises ValidationError on any banned node.
    """

    def _make_visit(msg: str) -> Callable[[ast.NodeVisitor, ast.AST], None]:
        def visit(self: ast.NodeVisitor, node: ast.AST) -> None:
            raise ValidationError(
                msg,
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )

        return visit

    visitor_methods: dict[str, object] = {
        f"visit_{node_type.__name__}": _make_visit(msg)
        for node_type, msg in messages.items()
    }
    visitor_cls = type("_Visitor", (ast.NodeVisitor,), visitor_methods)

    class _Validator:
        def validate(self, tree: ast.Module) -> None:
            visitor_cls().visit(tree)

    return _Validator
