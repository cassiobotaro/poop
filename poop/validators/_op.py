import ast
from collections.abc import Callable, Mapping
from typing import Any, ClassVar

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

type OpNode = ast.UnaryOp | ast.BoolOp | ast.Compare


def _ops(node: OpNode) -> list[ast.AST]:
    """The operators a node applies: one, or a comparison chain's several."""
    return list(node.ops) if isinstance(node, ast.Compare) else [node.op]


class _Visitor(ErrorCollector):
    def __init__(
        self,
        node_type: type[OpNode],
        messages: Mapping[type[ast.AST], str],
        allow: Callable[[Any], bool],
    ) -> None:
        super().__init__()
        self._node_type = node_type
        self._messages = messages
        self._allow = allow

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, self._node_type) and not self._allow(node):
            # `Compare` carries a list of ops, the others a single one. One
            # error per node, not per banned op: a chain reports once, at its
            # first banned operator.
            for op in _ops(node):
                message = self._messages.get(type(op))
                if message is not None:
                    self.report(message, node)
                    break
        self.generic_visit(node)


class OpValidator(CollectingValidator):
    """Forbids specific operators.

    A subclass sets `node_type` — the op-carrying node to inspect,
    ``ast.UnaryOp`` / ``ast.BoolOp`` (scalar ``node.op``) or ``ast.Compare``
    (``node.ops``) — and `messages`, mapping each banned operator type to its
    error. Overriding `allow` exempts a node, as unary ``-`` on a numeric
    literal is.
    """

    node_type: ClassVar[type[OpNode]]
    messages: ClassVar[Mapping[type[ast.AST], str]]

    def allow(self, node: Any) -> bool:
        return False

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(self.node_type, self.messages, self.allow), tree)
