from typing import TYPE_CHECKING

from poop.validators.base import CollectingValidator, ErrorCollector
from poop.validators.no_dunder_attribute import dunder_message

if TYPE_CHECKING:
    import ast


class _Visitor(ErrorCollector):
    """Reports every bare dunder name, labelled by the scope it stands in.

    The label used to read `dunder globals` wherever the name sat, so a
    class-body `__slots__ = ("a",)` was refused as a global. The scope is
    the innermost `class` or `def` the name is under: a class body makes it
    a class attribute, a function body a local, and the module a global.
    """

    def __init__(self) -> None:
        super().__init__()
        self._scopes: list[str] = []

    def _under(self, scope: str, node: ast.AST) -> None:
        self._scopes.append(scope)
        self.generic_visit(node)
        self._scopes.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._under("class attribute", node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._under("local", node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._under("local", node)

    def visit_Name(self, node: ast.Name) -> None:
        # Load *and* Store: `__builtins__.clear()` reads a live native, and
        # `__name__ = x` rebinds one. Both spellings are the same escape.
        scope = self._scopes[-1] if self._scopes else "global"
        message = dunder_message(node.id, dotted=False, scope=scope)
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

    visitor = _Visitor
