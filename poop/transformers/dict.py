import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers._collection import CollectionRewriter
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types._unwrap import _faithful
from poop.types.dict import Dict
from poop.types.exceptions import MIRRORS
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


def _poop_dict_from_kwargs(raw: dict[str, Object]) -> Dict:
    """Wrap a `**kwargs` parameter (a raw `dict` with `str` keys, POOP
    values) as a POOP `Dict` with `Str` keys."""
    d = Dict()
    for k, v in raw.items():
        d._data[Str(k)] = v
    return d


def _poop_kwargs_from(mapping: object) -> object:
    """The inverse of `_poop_dict_from_kwargs`, for a `f(**d)` call site.

    CPython's `**` demands raw `str` keys, and a POOP `Dict` carries `Str`
    ones — the constraint the `dict(**other)` branch below already works
    around. Every other splat position was covered (`f(*xs)` by `Tuple` being
    iterable, `def m(**kw)` by the varargs prologue, `{**a, **b}` by the merge
    helper); this was the one left, and it failed in Python's words about a
    POOP object: `TypeError: keywords must be strings`.

    Keys unwrap through the faithful idiom: a non-`Str` key reaches CPython
    raw, so `f(**{1: 2})` still answers `keywords must be strings` — true, and
    now about a key the program actually wrote. A non-mapping argument is
    returned untouched for the same reason, so `f(**5)` answers CPython's own
    `argument after ** must be a mapping, not int`. Values stay POOP objects;
    a `**kw` parameter on the other side re-wraps them into a `Dict`.
    """
    from poop.types.mapping_proxy import MappingProxy

    if isinstance(mapping, MappingProxy):
        mapping = mapping._dict
    if not isinstance(mapping, Dict):
        return mapping
    return {_faithful(key): value for key, value in mapping._data.items()}


def _poop_dict_merge(*parts: Dict) -> Dict:
    """Merge POOP `Dict`s left to right for a `{**a, **b, ...}` display.

    Later parts override earlier keys, matching CPython's `**` merge.
    """
    d = Dict()
    for part in parts:
        if not isinstance(part, Dict):
            raise MIRRORS["TypeError"](
                f"cannot ** -unpack {type(part).__qualname__} into a dict display"
            )
        d._data.update(part._data)
    return d


def _poop_dict_from(*args: object, **kwargs: Object) -> Dict:
    refuse_extra_arguments(
        "dict",
        args,
        kwargs,
        most=1,
        built_from="at most one mapping or sequence of pairs",
        hint="write a literal for entries",
        # The one constructor that takes them: `dict(a=1)`.
        keywords=True,
    )
    arg = args[0] if args else None
    if arg is None:
        d = Dict()
    elif isinstance(arg, Dict):
        d = arg.copy()
    elif isinstance(arg, Iterable):
        d = Dict()
        for item in cast("Iterable[Object]", arg):
            if isinstance(item, (Tuple, List)):
                if len(item._items) != 2:
                    raise MIRRORS["TypeError"](
                        f"dict entry must have exactly 2 elements, got {len(item._items)}"
                    )
                d._data[item._items[0]] = item._items[1]
            else:
                raise MIRRORS["TypeError"](
                    f"cannot use {type(item).__qualname__} as dict entry"
                )
    else:
        raise MIRRORS["TypeError"](f"cannot convert {type(arg).__qualname__} to dict")
    # dict(a=1, b=2) / dict(mapping, a=1): keyword names become Str keys.
    for k, v in kwargs.items():
        d._data[Str(k)] = v
    return d


class _DictRewriter(CollectionRewriter):
    builtin = "dict"
    call_target = "_poop_dict_from"
    name_target = "_poop_dict_cls"

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Unlike the other collection builtins, dict(...) accepts keywords
        # (dict(a=1, b=2)). Forward named keywords to _poop_dict_from.
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
        # A `**x` splat (kw.arg is None) cannot reach the bare `_poop_dict`
        # class: Python's `**` unpacking demands raw `str` keys, but a POOP
        # Dict carries `Str` keys, so `_poop_dict(**other)` raises
        # "keywords must be strings". Fold the call into a `_poop_dict_merge`
        # instead — the same machinery a `{**a, 'k': v}` display uses — so
        # `dict(other, x=1, **more)` merges left to right like CPython.
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == self.builtin
            and len(node.args) <= 1
            and any(kw.arg is None for kw in node.keywords)
        ):
            # A positional arg may be a mapping or an iterable of pairs;
            # normalise it through `_poop_dict_from` so `_poop_dict_merge`
            # always sees a Dict part.
            parts: list[ast.expr] = [
                ast.Call(
                    func=ast.Name(id="_poop_dict_from", ctx=ast.Load()),
                    args=[self.visit(arg)],
                    keywords=[],
                )
                for arg in node.args
            ]
            # A named keyword is a plain pair; `**x` (kw.arg is None) is a
            # splat. The StrTransformer has already run, so wrap the keyword
            # name in `_poop_str` ourselves to give the merged Dict a `Str`
            # key (matching `_poop_dict_from`'s kwargs handling).
            entries: list[tuple[ast.expr | None, ast.expr]] = [
                (None, self.visit(kw.value))
                if kw.arg is None
                else (
                    ast.Call(
                        func=ast.Name(id="_poop_str", ctx=ast.Load()),
                        args=[ast.Constant(value=kw.arg)],
                        keywords=[],
                    ),
                    self.visit(kw.value),
                )
                for kw in node.keywords
            ]
            return self._merge_call(self._fold_parts(entries, node, parts), node)
        return super().visit_Call(node)

    def _fold_parts(
        self,
        entries: Iterable[tuple[ast.expr | None, ast.expr]],
        ref: ast.AST,
        parts: list[ast.expr],
    ) -> list[ast.expr]:
        """Fold (key, value) entries into `_poop_dict_merge` arguments.

        A `None` key marks a `**x` splat: it flushes the pending run of
        plain pairs into a `_poop_dict_from_pairs(...)` part, then appends
        `x` whole. Shared by the `dict(a, **b)` call path and the
        `{**a, 'k': v}` display path so both fold identically.
        """
        pending: list[ast.expr] = []
        for key, value in entries:
            if key is None:
                if pending:
                    parts.append(self._pairs_call(pending, ref))
                    pending = []
                parts.append(value)
            else:
                pending.append(key)
                pending.append(value)
        if pending:
            parts.append(self._pairs_call(pending, ref))
        return parts

    @staticmethod
    def _merge_call(parts: list[ast.expr], ref: ast.AST) -> ast.expr:
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_dict_merge", ctx=ast.Load()),
                args=parts,
                keywords=[],
            ),
            ref,
        )

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
        return self._merge_call(
            self._fold_parts(zip(node.keys, node.values), node, []), node
        )


class DictTransformer(BaseTransformer):
    rewriter = _DictRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_dict": Dict,
        "_poop_dict_cls": builtin_alias(Dict, _poop_dict_from, "dict"),
        "_poop_dict_from_pairs": _poop_dict_from_pairs,
        "_poop_dict_from": _poop_dict_from,
        "_poop_dict_merge": _poop_dict_merge,
        "_poop_dict_from_kwargs": _poop_dict_from_kwargs,
        "_poop_kwargs_from": _poop_kwargs_from,
    }
