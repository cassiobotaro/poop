import ast
from collections.abc import Iterable
from itertools import batched, chain, groupby
from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter, call_at
from poop.types import mirrors
from poop.types._alias import builtin_alias
from poop.types._mapping import _MappingMixin
from poop.types._message import article
from poop.types._raw import _faithful
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_dict_from_pairs(*pairs: Object) -> Dict:
    # The rewrite always hands over an even run of key, value; `strict` makes a
    # stray odd element a failure rather than a silently dropped key.
    d = Dict()
    for k, v in batched(pairs, 2, strict=True):
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
    `Value after ** must be a mapping, not int`. Values stay POOP objects;
    a `**kw` parameter on the other side re-wraps them into a `Dict`.
    """
    if isinstance(mapping, MappingProxy):
        mapping = mapping._dict
    if not isinstance(mapping, _MappingMixin):
        return mapping
    return {_faithful(key): value for key, value in mapping._data.items()}


def _poop_dict_merge(*parts: Dict) -> Dict:
    """Merge POOP `Dict`s left to right for a `{**a, **b, ...}` display.

    Later parts override earlier keys, matching CPython's `**` merge.
    """
    d = Dict()
    for part in parts:
        if not isinstance(part, _MappingMixin):
            # The mapping twin of `_collection.spread`, and the same sentence.
            # This one was POOP's own and still wrong in two smaller ways: `**
            # -unpack` carries a stray space, and "dict display" is Python's
            # grammar vocabulary for a construct POOP calls a literal.
            raise mirrors.TypeError(
                f"a dict literal can only spread a mapping, "
                f"got {article(type(part).__qualname__)}"
            )
        d._data.update(part._data)
    return d


def _entries(arg: object, kind: str, kwargs: dict[str, Object]) -> dict[Object, Object]:
    """The raw entries `dict(arg, **kwargs)` builds from, for either kind.

    `kind` is the constructor the program wrote, for the refusals: `frozendict`
    is built from exactly what `dict` is, and answers its own name.
    """
    data: dict[Object, Object]
    if arg is None:
        data = {}
    elif isinstance(arg, _MappingMixin):
        data = arg._data.copy()
    elif isinstance(arg, Iterable):
        data = {}
        for item in cast("Iterable[Object]", arg):
            if isinstance(item, (Tuple, List)):
                if len(item._items) != 2:
                    raise mirrors.TypeError(
                        f"{kind} entry must have exactly 2 elements, got {len(item._items)}"
                    )
                data[item._items[0]] = item._items[1]
            else:
                raise mirrors.TypeError(
                    f"cannot use {type(item).__qualname__} as {kind} entry"
                )
    else:
        raise mirrors.TypeError(f"cannot convert {type(arg).__qualname__} to {kind}")
    # dict(a=1, b=2) / dict(mapping, a=1): keyword names become Str keys.
    for k, v in kwargs.items():
        data[Str(k)] = v
    return data


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
    return Dict._wrapping(_entries(args[0] if args else None, "dict", kwargs))


class _DictRewriter(BuiltinRewriter):
    builtin = "dict"
    call_target = "_poop_dict_from"
    name_target = "_poop_dict_cls"

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # A `**x` splat (kw.arg is None) cannot reach the bare `_poop_dict`
        # class: Python's `**` unpacking demands raw `str` keys, but a POOP
        # Dict carries `Str` keys, so `_poop_dict(**other)` raises
        # "keywords must be strings". Fold the call into a `_poop_dict_merge`
        # instead — the same machinery a `{**a, 'k': v}` display uses — so
        # `dict(other, x=1, **more)` merges left to right like CPython.
        if (
            isinstance(node.func, ast.Name)
            and self.is_builtin(node.func.id)
            and len(node.args) <= 1
            and any(kw.arg is None for kw in node.keywords)
        ):
            # A positional arg may be a mapping or an iterable of pairs;
            # normalise it through `_poop_dict_from` so `_poop_dict_merge`
            # always sees a Dict part.
            parts: list[ast.expr] = [
                call_at("_poop_dict_from", [self.visit(arg)], arg) for arg in node.args
            ]
            # A named keyword is a plain pair; `**x` (kw.arg is None) is a
            # splat. The StrTransformer has already run, so wrap the keyword
            # name in `_poop_str` ourselves to give the merged Dict a `Str`
            # key (matching `_poop_dict_from`'s kwargs handling).
            entries: list[tuple[ast.expr | None, ast.expr]] = [
                (None, self.visit(kw.value))
                if kw.arg is None
                else (
                    call_at("_poop_str", [ast.Constant(value=kw.arg)], kw.value),
                    self.visit(kw.value),
                )
                for kw in node.keywords
            ]
            return self._merge_call([*parts, *self._fold_parts(entries, node)], node)
        return super().visit_Call(node)

    def _fold_parts(
        self, entries: Iterable[tuple[ast.expr | None, ast.expr]], ref: ast.AST
    ) -> list[ast.expr]:
        """Fold (key, value) entries into `_poop_dict_merge` arguments.

        A `None` key marks a `**x` splat, which stays `x` whole; each run of
        plain pairs between splats becomes one `_poop_dict_from_pairs(...)`.
        Shared by the `dict(a, **b)` call path and the `{**a, 'k': v}` display
        path so both fold identically.
        """
        parts: list[ast.expr] = []
        for is_splat, run in groupby(entries, key=lambda entry: entry[0] is None):
            if is_splat:
                parts.extend(value for _, value in run)
            else:
                pairs = cast("Iterable[tuple[ast.expr, ast.expr]]", run)
                parts.append(self._pairs_call(list(chain.from_iterable(pairs)), ref))
        return parts

    @staticmethod
    def _merge_call(parts: list[ast.expr], ref: ast.AST) -> ast.expr:
        return call_at("_poop_dict_merge", parts, ref)

    @staticmethod
    def _pairs_call(flat: list[ast.expr], ref: ast.AST) -> ast.expr:
        return call_at("_poop_dict_from_pairs", flat, ref)

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        self.generic_visit(node)
        entries = list(zip(node.keys, node.values, strict=True))
        if all(k is not None for k in node.keys):
            # No splat: one `_poop_dict_from_pairs`, without a merge around it.
            pairs = cast("list[tuple[ast.expr, ast.expr]]", entries)
            return self._pairs_call(list(chain.from_iterable(pairs)), node)
        # A `**x` entry (key is None) makes this a merge: each run of plain
        # pairs becomes a _poop_dict_from_pairs(...), each **x stays as x,
        # and _poop_dict_merge folds them left to right.
        return self._merge_call(self._fold_parts(entries, node), node)


class DictTransformer(BaseTransformer):
    rewriter = _DictRewriter
    BINDINGS = {
        "_poop_dict": Dict,
        "_poop_dict_cls": builtin_alias(Dict, _poop_dict_from, "dict"),
        "_poop_dict_from_pairs": _poop_dict_from_pairs,
        "_poop_dict_from": _poop_dict_from,
        "_poop_dict_merge": _poop_dict_merge,
        "_poop_dict_from_kwargs": _poop_dict_from_kwargs,
        "_poop_kwargs_from": _poop_kwargs_from,
    }
