import ast
from typing import TYPE_CHECKING, ClassVar

from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

if TYPE_CHECKING:
    from poop.errors import ValidationError


class _Visitor(ErrorCollector):
    def __init__(self, protected: frozenset[str], message: str) -> None:
        super().__init__()
        self._protected = protected
        self._message = message
        self._in_class_body = False

    def _check(self, name: str, node: ast.AST) -> None:
        if name in self._protected:
            self.report(self._message.format(name=name), node)

    def visit_Name(self, node: ast.Name) -> None:
        # Every name a statement binds is a `Name` in `Store` context: `x = ...`,
        # `x: T = ...`, `x += ...`, each name of an unpacking (`x, *y = ...`),
        # and the targets of `for`, `with ... as` and `:=`. `generic_visit`
        # already walks into the tuples, lists and stars around them.
        if isinstance(node.ctx, ast.Store):
            self._check(node.id, node)

    def visit_arg(self, node: ast.arg) -> None:
        # A parameter named after a namespace binding shadows it inside the
        # body exactly like a local assignment does, so `def m(self, Try):`
        # makes `Try(...)` inside it call the argument. Every parameter of a
        # def or a lambda — `*args` and `**kwargs` included — is an `arg`;
        # lambdas are POOP's block form and carry most user code.
        self._check(node.arg, node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node.name, node)
        outer = self._in_class_body
        self._in_class_body = True
        self.generic_visit(node)
        self._in_class_body = outer

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # A def directly in a class body is a method: it binds as a class
        # attribute, not in the namespace scope, so `class Calc: def Try(self)`
        # stays allowed. A def anywhere else binds a real local name and
        # shadows the binding exactly like `Try = ...` does. `no_free_functions`
        # refuses such a def, but every validator collects (`--validators-only`
        # reports all of them), so this one still names the shadowing.
        if not self._in_class_body:
            self._check(node.name, node)
        outer = self._in_class_body
        self._in_class_body = False
        self.generic_visit(node)
        self._in_class_body = outer

    visit_FunctionDef = visit_AsyncFunctionDef = _visit_function


class ShadowValidator(CollectingValidator):
    """Forbids rebinding a protected name.

    Every position that binds a name is checked — an assignment target, a
    parameter of a def or a lambda, a class name, a def outside a class body
    — because a rebinding in any of them retargets whatever the name stood
    for. The fourth shared shape beside `CallNameValidator`, `NodeValidator`
    and `OpValidator`: `no_builtin_shadow` and `no_namespace_shadow` wrote
    the same visitor, constructor and `collect` and differed in the two
    attributes below.

    A subclass sets `protected` and `message`; `{name}` in the message is the
    name that was rebound.
    """

    protected: ClassVar[frozenset[str]]
    message: ClassVar[str]

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(self.protected, self.message), tree, self.name)
