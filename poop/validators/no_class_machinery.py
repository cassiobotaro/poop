from typing import TYPE_CHECKING

from poop.validators.base import CollectingValidator, ErrorCollector
from poop.validators.no_decorator import ALLOWED as _DECORATORS

if TYPE_CHECKING:
    import ast

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
_SUPER_IN_LAMBDA = (
    "super() inside a lambda is forbidden — send it from the method and hand "
    "the block its answer"
)
_INIT_RETURNS = (
    "return with a value in __init__ is forbidden — __init__ builds the "
    "receiver and answers nothing"
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

    Two positions are refused by what *encloses* them, read off a stack of
    the functions being descended. `super()` under a `lambda` has no class
    cell — a lambda owns none — and CPython answered `RuntimeError: super():
    no arguments` at run time, about a cell the block cannot be given. A
    `return` with a value directly in an `__init__` body answered
    `TypeError: __init__() should return None, not 'int'`; the return
    transformer skips `__init__` for that reason, so nothing else looked.
    """

    def __init__(self) -> None:
        super().__init__()
        self._decorators: set[ast.AST] = set()
        self._callees: set[ast.AST] = set()
        # The enclosing functions, innermost last: a `def`'s name, or
        # `"<lambda>"` as CPython itself names one.
        self._enclosing: list[str] = []

    def _within(self, name: str, node: ast.AST) -> None:
        self._enclosing.append(name)
        self.generic_visit(node)
        self._enclosing.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._decorators.update(node.decorator_list)
        self.generic_visit(node)

    def _visit_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._decorators.update(node.decorator_list)
        self._within(node.name, node)

    # Every node that carries a `decorator_list`.
    visit_FunctionDef = visit_AsyncFunctionDef = _visit_def

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._within("<lambda>", node)

    def visit_Return(self, node: ast.Return) -> None:
        if node.value is not None and self._enclosing[-1:] == ["__init__"]:
            self.report(_INIT_RETURNS, node)
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
            elif self._enclosing[-1:] == ["<lambda>"]:
                self.report(_SUPER_IN_LAMBDA, node)
            return
        if node not in self._decorators:
            self.report(_DECORATOR_ONLY.format(name=node.id), node)


class NoClassMachineryValidator(CollectingValidator):
    visitor = _Visitor
