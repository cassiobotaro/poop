import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

# The three `INFECTIONS.md` reasons about and allows: "class-definition
# decorators, not runtime operations on values". They are also exactly the
# three non-machinery entries in `_ALLOWED_BUILTINS`, so the intended surface
# was already written down twice — and checked nowhere.
ALLOWED = ("staticmethod", "classmethod", "property")


class NoDecoratorValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_NoDecoratorVisitor(), tree)


def _spelling(node: ast.expr) -> str:
    """How the decorator was written, for the message that refuses it."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_spelling(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return f"{_spelling(node.func)}(...)"
    return ast.unparse(node)


class _NoDecoratorVisitor(ErrorCollector):
    """Refuses every decorator but the three class-definition ones.

    `@` applies an arbitrary expression, which is a function call written as
    syntax rather than sent as a message — the shape `no_subscript`,
    `no_fstring` and `no_if` exist to remove. Nothing enforced the boundary,
    so a plain block silently replaced a method:

        twice = lambda f: (lambda: 2)

        class Foo(Object):
            @twice
            def bar():
                return 1

        Foo.bar().print()   ->  2

    A bare `ast.Name` among the three is the whole allowance: `@property` is
    accepted, `@property(...)`, `@a.b` and `@twice` are not. The call form is
    refused even for the three — `@staticmethod(...)` is a runtime call, which
    is the distinction the allowance rests on.
    """

    def _check(
        self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ALLOWED:
                continue
            self.report(
                f"decorator @{_spelling(decorator)} is forbidden — "
                f"send the message instead; only @{', @'.join(ALLOWED)} are allowed",
                decorator,
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # `async def` is rejected by `no_async` in its own right, but a
        # decorator on one must not slip through on the way.
        self._check(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node)
        self.generic_visit(node)
