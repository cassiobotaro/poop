import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer


def _rebind(name: str, helper: str) -> ast.Assign:
    """`<name> = <helper>(<name>)` — convert a variadic parameter to POOP."""
    return ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id=helper, ctx=ast.Load()),
            args=[ast.Name(id=name, ctx=ast.Load())],
            keywords=[],
        ),
    )


def _prologue(args: ast.arguments) -> list[ast.stmt]:
    stmts: list[ast.stmt] = []
    if args.vararg is not None:
        stmts.append(_rebind(args.vararg.arg, "_poop_tuple_from"))
    if args.kwarg is not None:
        stmts.append(_rebind(args.kwarg.arg, "_poop_dict_from_kwargs"))
    return stmts


class _VarargsRewriter(ast.NodeTransformer):
    """Carry the variadic calling convention across both ends of a call.

    CPython packs variadic parameters natively: inside `def m(self, *args,
    **kw)`, `args` is a raw `tuple` and `kw` a raw `dict` with raw `str`
    keys, so every POOP message on them crashes. Inject a prologue
    (`args = _poop_tuple_from(args)`, `kw = _poop_dict_from_kwargs(kw)`) as
    the first body statements; for lambdas (no statement body), wrap the
    expression in a nested lambda that receives the converted values.

    The **call site** is the other end of that round trip, and it needed the
    conversion run the other way — see `visit_Call`.
    """

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Unwrap a `**d` splat's keys so CPython's `**` accepts them.

        Three of the four splat positions already worked: `f(*xs)` because a
        POOP `Tuple` is iterable, `def m(**kw)` by the prologue above, and
        `{**a, **b}` through `_poop_dict_merge`. The call site was the one
        left, and it failed in Python's own words about a POOP object —

            d = {"a": 1}
            A().m(**d)      # TypeError: keywords must be strings

        — because `**` demands raw `str` keys and a POOP `Dict` carries `Str`.
        `DictTransformer` had already met the constraint for `dict(**other)`
        and worked around it there; this generalises the same fix to every
        call. It has to run after that transformer (and after
        `RaiseTransformer`, whose `_poop_raise(Exc, **kw)` this then covers),
        which the declaration order in `__init__.py` guarantees.
        """
        self.generic_visit(node)
        for kw in node.keywords:
            if kw.arg is None:
                kw.value = ast.copy_location(
                    ast.Call(
                        func=ast.Name(id="_poop_kwargs_from", ctx=ast.Load()),
                        args=[kw.value],
                        keywords=[],
                    ),
                    kw.value,
                )
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._rewrite_function(node)

    def _rewrite_function(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        prologue = _prologue(node.args)
        if prologue:
            node.body = prologue + node.body
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        self.generic_visit(node)
        names: list[tuple[str, str]] = []
        if node.args.vararg is not None:
            names.append((node.args.vararg.arg, "_poop_tuple_from"))
        if node.args.kwarg is not None:
            names.append((node.args.kwarg.arg, "_poop_dict_from_kwargs"))
        if not names:
            return node
        # lambda <params>: body  ->
        # lambda <params>: (lambda xs, kw: body)(conv(xs), conv(kw))
        inner = ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg=name) for name, _ in names],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=node.body,
        )
        call = ast.Call(
            func=inner,
            args=[
                ast.Call(
                    func=ast.Name(id=helper, ctx=ast.Load()),
                    args=[ast.Name(id=name, ctx=ast.Load())],
                    keywords=[],
                )
                for name, helper in names
            ],
            keywords=[],
        )
        node.body = call
        return node


class VarargsTransformer(BaseTransformer):
    """Rebinds variadic parameters to POOP types.

    `_poop_tuple_from` and `_poop_dict_from_kwargs` are provided by the
    tuple and dict transformers.
    """

    rewriter = _VarargsRewriter
    BINDINGS: ClassVar[dict[str, object]] = {}
