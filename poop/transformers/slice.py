from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.slice import Slice

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.none import NoneClass


def _poop_slice_from(*args: object, **kwargs: object) -> Slice:
    """`slice(...)`, guarded. Without this factory the call would reach
    `Slice(...)` itself, whose refusal names `__init__`, a dunder
    `no_dunder_attribute` refuses, from a construct the program spelled
    without a dunder anywhere.
    """
    refuse_extra_arguments(
        "slice",
        args,
        kwargs,
        most=3,
        built_from="a stop, or a start and a stop and an optional step",
        hint="write slice(stop) or slice(start, stop, step)",
        empty=False,
    )
    # CPython's one-argument `slice(stop)` means `slice(None, stop, None)`: the
    # lone argument is the stop, not the start. Counted here, on the values the
    # call received, and not on the expressions written: a starred argument is
    # one node carrying any number of values, so `slice(*xs)` with `xs = (1,
    # 5)` is `slice(1, 5)`
    # (`doc/adr/0069-a-constructor-call-is-read-by-its-converter-at-run-time.md`).
    if len(args) == 1:
        args = (None, *args)
    return Slice(*cast("tuple[Index | NoneClass | None, ...]", args))


class _SliceRewriter(BuiltinRewriter):
    builtin = "slice"
    call_target = "_poop_slice_from"
    # The alias, as every sibling constructor binds: a bare `slice` naming the
    # class itself would build `s = slice; s(5)` and `class S(slice)` through
    # `Slice.__init__` — where the lone argument is the *start* — and silently
    # answer `slice(5, None, None)` for the spelling that answers
    # `slice(None, 5, None)` when called by name.
    name_target = "_poop_slice_cls"


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS = {
        "_poop_slice_cls": builtin_alias(Slice, _poop_slice_from, "slice"),
        "_poop_slice_from": _poop_slice_from,
    }
