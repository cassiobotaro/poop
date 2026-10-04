import ast
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

from poop.types.exceptions import MIRRORS

if TYPE_CHECKING:
    from collections.abc import Iterable


class Transformer(Protocol):
    def transform(self, tree: ast.Module) -> ast.Module: ...


class BaseTransformer:
    """Base class for AST transformers.

    Subclasses set, as plain class attributes (annotated once, here):
    - rewriter: the NodeTransformer class to use
    - BINDINGS: dict of names to inject into the namespace (optional)
    """

    rewriter: ClassVar[type[ast.NodeTransformer]]
    BINDINGS: ClassVar[dict[str, object]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        # At class definition, as `CollectingValidator` checks its `visitor`:
        # otherwise a transformer that forgot one failed on the first program.
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "rewriter"):
            raise MIRRORS["TypeError"](f"{cls.__name__} sets no `rewriter`")

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = self.rewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


def name_at(name: str, node: ast.AST, ctx: ast.expr_context | None = None) -> ast.Name:
    """`name`, positioned where `node` was — a load unless `ctx` says otherwise."""
    return ast.copy_location(ast.Name(id=name, ctx=ctx or ast.Load()), node)


def call_at(
    target: str,
    args: Iterable[ast.expr],
    node: ast.AST,
    keywords: Iterable[ast.keyword] = (),
) -> ast.Call:
    """`target(*args, **keywords)`, positioned where `node` was.

    Every rewrite in this package replaces one node with a call to a binding,
    and each spelt out `copy_location(Call(func=Name(...), ...), node)` by hand.
    """
    return ast.copy_location(
        ast.Call(func=name_at(target, node), args=list(args), keywords=list(keywords)),
        node,
    )


class BuiltinRewriter(ast.NodeTransformer):
    """Routes `<builtin>(...)` to its converter and a bare `<builtin>` to its class.

    Every constructor builtin POOP rewrites has these two positions. A call goes
    to `call_target` with every argument and keyword forwarded, whatever the
    arity, so the converter refuses a bad call in POOP's words; any other
    mention becomes `name_target`, which keeps `class Foo(list)` and
    `x.is_instance(int)` naming the class.
    """

    builtin: ClassVar[str]
    call_target: ClassVar[str]
    name_target: ClassVar[str]

    def is_builtin(self, name: str) -> bool:
        return name == self.builtin

    def call_args(self, node: ast.Call) -> list[ast.expr]:
        """The converter's positional arguments; a hook for `slice`."""
        return [self.visit(arg) for arg in node.args]

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and self.is_builtin(node.func.id):
            keywords = [
                ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                for kw in node.keywords
            ]
            return call_at(self.call_target, self.call_args(node), node, keywords)
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if self.is_builtin(node.id):
            return name_at(self.name_target, node, node.ctx)
        return node
