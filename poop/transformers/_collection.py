"""Shared machinery for the collection transformers.

``list``/``tuple``/``set``/``frozenset``/``dict`` route ``<builtin>(x)``
and a bare ``<builtin>`` through ``BuiltinRewriter`` like every other
constructor; what is theirs is the literal — wrapping ``[a, b]`` in the POOP
constructor binding, spreads included — and the converter factories.
"""

import ast
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import call_at
from poop.types._message import article
from poop.types.exceptions import MIRRORS
from poop.types.range import Range

if TYPE_CHECKING:
    from poop.types.object import Object


def spread(value: object, kind: str) -> object:
    """`value`, or a refusal naming the literal the reader actually wrote.

    `[*5]`, `(*5,)` and `{*5}` are literals with a spread, and all three
    answered in terms of a constructor call the program never wrote:

        [*5]     # list() argument after * must be an iterable, not int

    `list()` is a message spelt as a call, which the wording sweep bans; it
    names a construct absent from the source, since the reader wrote brackets;
    and `[*5]` is not even routed through the `list` converter, so the name was
    doubly not the one that ran.

    The block form was already right and is the target this copies: `f(*5)`
    answers `<block> argument after * must be an iterable, not int`, naming the
    receiver in POOP's own spelling.
    """
    if isinstance(value, Iterable):
        return value

    raise MIRRORS["TypeError"](
        f"a {kind} literal can only spread a collection, "
        f"got {article(type(value).__qualname__)}"
    )


def _spread_elts(elts: list[ast.expr], kind: str) -> list[ast.expr]:
    """Each starred element routed through `spread`, the rest untouched."""
    return [
        ast.copy_location(
            ast.Starred(
                value=call_at("_poop_spread", [elt.value, ast.Constant(kind)], elt),
                ctx=elt.ctx,
            ),
            elt,
        )
        if isinstance(elt, ast.Starred)
        else elt
        for elt in elts
    ]


def wrap_elts(node: ast.List | ast.Tuple | ast.Set, target: str) -> ast.Call:
    return call_at(target, _spread_elts(node.elts, _LITERAL_KIND[type(node)]), node)


# What the reader wrote, for `spread`'s sentence — never the converter's name.
_LITERAL_KIND: dict[type[ast.AST], str] = {
    ast.List: "list",
    ast.Tuple: "tuple",
    ast.Set: "set",
}


def make_constructor[T](poop_type: type[T]) -> Callable[..., T]:
    def _constructor(*elements: Object) -> T:
        return poop_type(*elements)

    return _constructor


def make_iterable_from[T](
    poop_type: type[T], *, copy: bool = False
) -> Callable[..., T]:
    def _from(*args: object, **kwargs: object) -> T:
        refuse_extra_arguments(
            poop_type.__name__,
            args,
            kwargs,
            most=1,
            built_from="at most one collection",
            hint="write a literal for elements",
        )
        arg = args[0] if args else None
        if arg is None:
            return poop_type()
        if isinstance(arg, poop_type):
            # Mutable collections must not alias their source; CPython's
            # tuple(t) / frozenset(fs) do return the same object.
            if copy:
                return poop_type(*cast("Iterable[Object]", arg))
            return arg
        if isinstance(arg, Range):
            return poop_type(*arg._iter())
        if isinstance(arg, Iterable):
            return poop_type(*cast("Iterable[Object]", arg))
        # Both names come off the cloak, never a literal: a hand-written
        # "List" would say `cannot convert int to List`, half the sentence
        # in POOP's vocabulary and half in the wrapper's.
        raise MIRRORS["TypeError"](
            f"cannot convert {type(arg).__qualname__} to {poop_type.__name__}"
        )

    return _from
