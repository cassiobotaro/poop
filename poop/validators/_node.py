from typing import TYPE_CHECKING, ClassVar

from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

if TYPE_CHECKING:
    import ast
    from collections.abc import Mapping

    from poop.errors import ValidationError


class _Visitor(ErrorCollector):
    def __init__(self, messages: Mapping[type[ast.AST], str]) -> None:
        super().__init__()
        self._messages = messages

    def visit(self, node: ast.AST) -> None:
        message = self._messages.get(type(node))
        if message is not None:
            self.report(message, node)
        # Descend into the rejected node rather than stopping there: an `if`
        # nested in an `if` is two rewrites, and reporting only the outer one
        # leaves the reader to fix one, rerun, and only then meet the other.
        self.generic_visit(node)


class NodeValidator(CollectingValidator):
    """Forbids specific AST node types.

    A subclass sets `messages`, mapping each banned node type to the error it
    reports.
    """

    messages: ClassVar[Mapping[type[ast.AST], str]]

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(self.messages), tree, self.name)
