import ast

from poop.validators.base import CollectingValidator, ErrorCollector

# `await_` is not a method: `AwaitTransformer` rewrites every `x.await_()` to
# `await x`. Each use the rewrite cannot honour is refused here, before
# CPython would answer it with a raw `SyntaxError` about an `await` the
# program never wrote.
_SELECTOR = "await_"
_OUTSIDE = "'await' outside async function"
_NOT_ASYNC = f"{_OUTSIDE} — send await_() inside an async def method"
_IN_BLOCK = (
    f"{_OUTSIDE} — a block cannot await; let it answer the coroutine "
    "and send await_() to that answer"
)
_UNSENT = "await_ is a message — send it: x.await_()"
_RESERVED = (
    "await_ is reserved — POOP sends it to await a coroutine; "
    "name the method something else"
)

type _Scope = ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | ast.ClassDef


class _Visitor(ErrorCollector):
    def __init__(self) -> None:
        super().__init__()
        # The scopes enclosing the node being visited, innermost last. A
        # class body counts: CPython refuses an `await` in one even inside an
        # async method.
        self._scopes: list[_Scope] = []

    def _within(self, node: _Scope) -> None:
        self._scopes.append(node)
        self.generic_visit(node)
        self._scopes.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._within(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._within(node)

    def _visit_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if node.name == _SELECTOR:
            self.report(_RESERVED, node)
        self._within(node)

    visit_FunctionDef = visit_AsyncFunctionDef = _visit_def

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == _SELECTOR):
            self.generic_visit(node)
            return
        given = len(node.args) + len(node.keywords)
        if given:
            self.report(f"await_() takes no arguments ({given} given)", node)
        scope = self._scopes[-1] if self._scopes else None
        if isinstance(scope, ast.Lambda):
            self.report(_IN_BLOCK, node)
        elif not isinstance(scope, ast.AsyncFunctionDef):
            self.report(_NOT_ASYNC, node)
        # The receiver and the arguments, but not `func` itself: visiting the
        # attribute would report the sent selector as an unsent read.
        self.visit(func.value)
        for child in (*node.args, *node.keywords):
            self.visit(child)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == _SELECTOR:
            self.report(_UNSENT, node)
        self.generic_visit(node)


class NoMisplacedAwaitValidator(CollectingValidator):
    visitor = _Visitor
