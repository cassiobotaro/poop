import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors
from poop.validators.no_dunder_attribute import dunder_message


class _Visitor(ErrorCollector):
    def visit_Name(self, node: ast.Name) -> None:
        # Load *and* Store: `__builtins__.clear()` reads a live native, and
        # `__name__ = x` rebinds one. Both spellings are the same escape.
        message = dunder_message(node.id, dotted=False)
        if message is not None:
            self.report(message, node)


class NoDunderNameValidator(CollectingValidator):
    """Closes the `ast.Name` half of the dunder ban.

    `no_dunder_attribute` guards `x.__class__`; nothing guarded a bare
    `__builtins__`. Every dunder global CPython injects into an `exec`
    namespace is a naked Python native — and `__builtins__` is mutable, so
    `__builtins__.clear()` corrupts the interpreter. Stripping the namespace
    is no fix: `exec` re-injects `__builtins__` regardless of what the
    namespace dict holds, so the guard has to live at validation time.
    """

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(), tree)
