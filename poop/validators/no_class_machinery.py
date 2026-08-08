import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors
from poop.validators.no_decorator import ALLOWED as _DECORATORS

# The four non-dunder entries in `_ALLOWED_BUILTINS` (`poop/executor.py`).
# The other two, `__build_class__` and `__name__`, are dunders, and
# `no_dunder_name` already refuses them as a bare `ast.Name`.
_MACHINERY = frozenset({*_DECORATORS, "super"})

_DECORATOR_ONLY = (
    "{name} is forbidden here — it is class-definition machinery, "
    "usable only as a decorator (@{name})"
)
_SUPER_ONLY = (
    "super is forbidden here — call it; `super().method(...)` is the allowance"
)


class _Visitor(ErrorCollector):
    """Keeps the machinery allowance to the position it was argued for.

    `_ALLOWED_BUILTINS` admits these four as "language machinery with no
    message-passing substitute", and INFECTIONS.md scopes each one: `super` so
    inheritance works, the other three as decorators — "class-definition
    decorators, not runtime operations on values". `no_decorator` made the
    decorator half real. Everywhere else they stayed reachable as plain names,
    answering Python rather than POOP:

        property.print()   ->  AttributeError: type object 'property'
                               has no attribute 'print'

    which is the naked-native symptom the allow-list was introduced to end.
    One position stays open per name, and it is the one the allowance was
    granted for: a `decorator_list` entry for the three, the callee of a
    `Call` for `super`. The split is INFECTIONS.md's own — "`@property(...)`
    is refused even though `@property` is not, because a called decorator is a
    runtime operation, which is the distinction the allowance rests on" — so
    `property(getter)` is refused here for the reason `@property(...)` is
    refused there, and `staticmethod` never earns a call position either.
    """

    def __init__(self) -> None:
        super().__init__()
        self._decorators: set[ast.AST] = set()
        self._callees: set[ast.AST] = set()

    def _allow_decorators(
        self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        self._decorators.update(node.decorator_list)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._allow_decorators(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._allow_decorators(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._allow_decorators(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self._callees.add(node.func)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id not in _MACHINERY:
            return
        if node.id == "super":
            if node not in self._callees:
                self.report(_SUPER_ONLY, node)
            return
        if node not in self._decorators:
            self.report(_DECORATOR_ONLY.format(name=node.id), node)


class NoClassMachineryValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(), tree)
