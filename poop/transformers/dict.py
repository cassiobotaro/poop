import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._collection import CollectionRewriter
from poop.transformers.base import BaseTransformer
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_dict_from_pairs(*pairs: Object) -> Dict:
    d = Dict()
    it = iter(pairs)
    for k, v in zip(it, it):
        d._data[k] = v
    return d


def _poop_dict_merge(*parts: Dict) -> Dict:
    """Merge POOP `Dict`s left to right for a `{**a, **b, ...}` display.

    Later parts override earlier keys, matching CPython's `**` merge.
    """
    d = Dict()
    for part in parts:
        if not isinstance(part, Dict):
            raise TypeError(
                f"cannot ** -unpack {type(part).__qualname__} into a dict display"
            )
        d._data.update(part._data)
    return d


def _poop_dict_from(arg: object = None, **kwargs: Object) -> Dict:
    if arg is None:
        d = Dict()
    elif isinstance(arg, Dict):
        d = arg.copy()
    elif isinstance(arg, Iterable):
        d = Dict()
        for item in cast("Iterable[Object]", arg):
            if isinstance(item, (Tuple, List)):
                if len(item._items) != 2:
                    raise TypeError(
                        f"dict entry must have exactly 2 elements, got {len(item._items)}"
                    )
                d._data[item._items[0]] = item._items[1]
            else:
                raise TypeError(f"cannot use {type(item).__qualname__} as dict entry")
    else:
        raise TypeError(f"cannot convert {type(arg).__qualname__} to Dict")
    # dict(a=1, b=2) / dict(mapping, a=1): keyword names become Str keys.
    for k, v in kwargs.items():
        d._data[Str(k)] = v
    return d


class _DictRewriter(CollectionRewriter):
    builtin = "dict"
    call_target = "_poop_dict_from"
    name_target = "_poop_dict"

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Unlike the other collection builtins, dict(...) accepts keywords
        # (dict(a=1, b=2)). Forward named keywords to _poop_dict_from; a
        # ** splat (kw.arg is None) is left to the generic path.
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == self.builtin
            and len(node.args) <= 1
            and node.keywords
            and all(kw.arg is not None for kw in node.keywords)
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id=self.call_target, ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[
                        ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                        for kw in node.keywords
                    ],
                ),
                node,
            )
        return super().visit_Call(node)

    @staticmethod
    def _pairs_call(flat: list[ast.expr], ref: ast.AST) -> ast.expr:
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_dict_from_pairs", ctx=ast.Load()),
                args=flat,
                keywords=[],
            ),
            ref,
        )

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        self.generic_visit(node)
        if all(k is not None for k in node.keys):
            flat: list[ast.expr] = []
            for k, v in zip(node.keys, node.values):
                flat.append(cast("ast.expr", k))
                flat.append(v)
            return self._pairs_call(flat, node)
        # A `**x` entry (key is None) makes this a merge: each run of plain
        # pairs becomes a _poop_dict_from_pairs(...), each **x stays as x,
        # and _poop_dict_merge folds them left to right.
        parts: list[ast.expr] = []
        pending: list[ast.expr] = []
        for k, v in zip(node.keys, node.values):
            if k is None:
                if pending:
                    parts.append(self._pairs_call(pending, node))
                    pending = []
                parts.append(v)
            else:
                pending.append(k)
                pending.append(v)
        if pending:
            parts.append(self._pairs_call(pending, node))
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_dict_merge", ctx=ast.Load()),
                args=parts,
                keywords=[],
            ),
            node,
        )


class DictTransformer(BaseTransformer):
    rewriter = _DictRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_dict": Dict,
        "_poop_dict_from_pairs": _poop_dict_from_pairs,
        "_poop_dict_from": _poop_dict_from,
        "_poop_dict_merge": _poop_dict_merge,
    }
