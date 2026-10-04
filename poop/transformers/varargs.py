import ast

from poop.transformers.base import BaseTransformer, call_at, name_at

# Each variadic parameter and the helper that converts it — stated once for
# both `def` (a prologue) and `lambda` (a wrapping call).
_CONVERTERS = (("vararg", "_poop_tuple_from"), ("kwarg", "_poop_dict_from_kwargs"))


def _variadics(args: ast.arguments) -> list[tuple[str, str]]:
    """`(parameter name, converter)` for each variadic parameter `args` has."""
    found = []
    for slot, helper in _CONVERTERS:
        param = getattr(args, slot)
        if param is not None:
            found.append((param.arg, helper))
    return found


def _rebind(name: str, helper: str, node: ast.AST) -> ast.Assign:
    """`<name> = <helper>(<name>)` — convert a variadic parameter to POOP."""
    return ast.copy_location(
        ast.Assign(
            targets=[name_at(name, node, ast.Store())],
            value=call_at(helper, [name_at(name, node)], node),
        ),
        node,
    )


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
        which the declaration order in `_registry.py` guarantees.
        """
        self.generic_visit(node)
        for kw in node.keywords:
            if kw.arg is None:
                kw.value = call_at("_poop_kwargs_from", [kw.value], kw.value)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        prologue = [
            _rebind(name, helper, node) for name, helper in _variadics(node.args)
        ]
        node.body = prologue + node.body
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        self.generic_visit(node)
        names = _variadics(node.args)
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
                call_at(helper, [name_at(name, node)], node) for name, helper in names
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
