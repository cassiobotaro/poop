import ast
from collections.abc import Callable, Mapping
from typing import Any

from poop.errors import ValidationError


def make_op_validator(
    node_type: type[ast.AST],
    messages: Mapping[type[ast.AST], str],
    *,
    allow: Callable[[Any], bool] | None = None,
) -> type:
    """Factory for validators that forbid specific operators.

    Args:
        node_type: The op-carrying node to inspect — ``ast.UnaryOp`` /
            ``ast.BoolOp`` (scalar ``node.op``) or ``ast.Compare``
            (iterates ``node.ops`` and rejects the first banned op,
            preserving chained-comparison order).
        messages: Mapping from operator type (e.g. ``ast.Not``,
            ``ast.In``) to the error message raised when it appears.
        allow: Optional predicate on the visited node; when it returns
            True the node is skipped (e.g. unary ``-`` on a numeric
            literal is allowed).

    Returns:
        A Validator class that raises ValidationError on any banned op.
    """
    op_messages = dict(messages)
    is_compare = node_type is ast.Compare

    def _raise(node: ast.AST, message: str) -> None:
        raise ValidationError(
            message,
            lineno=getattr(node, "lineno", 0),
            col_offset=getattr(node, "col_offset", 0),
        )

    def _visit(self: ast.NodeVisitor, node: Any) -> None:
        if allow is None or not allow(node):
            if is_compare:
                for op in node.ops:
                    message = op_messages.get(type(op))
                    if message is not None:
                        _raise(node, message)
            else:
                message = op_messages.get(type(node.op))
                if message is not None:
                    _raise(node, message)
        self.generic_visit(node)

    visitor_cls = type(
        "_Visitor",
        (ast.NodeVisitor,),
        {f"visit_{node_type.__name__}": _visit},
    )

    class _Validator:
        def validate(self, tree: ast.Module) -> None:
            visitor_cls().visit(tree)

    return _Validator
