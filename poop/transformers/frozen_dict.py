from typing import TYPE_CHECKING

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.transformers.dict import _entries
from poop.types._alias import builtin_alias
from poop.types.frozen_dict import FrozenDict

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_frozendict_from(*args: object, **kwargs: Object) -> FrozenDict:
    """`frozendict(...)`: built from what `dict(...)` is built from."""
    refuse_extra_arguments(
        "frozendict",
        args,
        kwargs,
        most=1,
        built_from="at most one mapping or sequence of pairs",
        hint="write a dict literal for entries",
        keywords=True,
    )
    arg = args[0] if args else None
    # CPython answers the receiver itself for an exact frozendict with nothing
    # to add — `frozendict(fd) is fd` — as `frozenset(fs) is fs`.
    if type(arg) is FrozenDict and not kwargs:
        return arg
    return FrozenDict._wrapping(_entries(arg, "frozendict", kwargs))


class _FrozenDictRewriter(BuiltinRewriter):
    """`frozendict(...)` to its converter; the literal is a dict's, not this one's."""

    builtin = "frozendict"
    call_target = "_poop_frozendict_from"
    name_target = "_poop_frozendict_cls"


class FrozenDictTransformer(BaseTransformer):
    rewriter = _FrozenDictRewriter
    BINDINGS = {
        "_poop_frozendict_cls": builtin_alias(
            FrozenDict, _poop_frozendict_from, "frozendict"
        ),
        "_poop_frozendict_from": _poop_frozendict_from,
    }
