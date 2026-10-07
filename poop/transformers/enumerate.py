from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.enumerate import Enumerate

if TYPE_CHECKING:
    from poop.types.int import Int


def _poop_enumerate(*args: object, **kwargs: object) -> Enumerate:
    refuse_extra_arguments(
        "enumerate",
        args,
        kwargs,
        most=2,
        built_from="a collection and an optional start",
        hint="write enumerate(collection, start)",
        empty=False,
    )
    return Enumerate(args[0], cast("Int | None", args[1] if len(args) > 1 else None))


class _EnumerateRewriter(BuiltinRewriter):
    builtin = "enumerate"
    call_target = "_poop_enumerate"
    name_target = "_poop_enumerate_cls"


class EnumerateTransformer(BaseTransformer):
    rewriter = _EnumerateRewriter
    BINDINGS = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_enumerate_cls": builtin_alias(Enumerate, _poop_enumerate, "enumerate"),
    }
