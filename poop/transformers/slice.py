from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types.slice import Slice

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.none import NoneClass


def _poop_slice_from(*args: object, **kwargs: object) -> Slice:
    """`slice(...)`, guarded. `Slice(...)` *is* the call, so unlike its
    siblings this one had no factory at all — and the
    refusal that leaked was the sharpest of the eight, naming `__init__`, a
    dunder `no_dunder_attribute` refuses, from a construct the program spelled
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
    # call received, and not on the expressions written: the rewriter used to
    # insert the `None` when it saw one argument node, and a starred argument
    # is one node carrying any number of values, so `slice(*xs)` with `xs =
    # (1, 5)` was folded into `slice(None, 1, 5)`.
    if len(args) == 1:
        args = (None, *args)
    return Slice(*cast("tuple[Index | NoneClass | None, ...]", args))


class _SliceRewriter(BuiltinRewriter):
    builtin = "slice"
    call_target = "_poop_slice_from"
    name_target = "_poop_slice"


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS = {
        "_poop_slice": Slice,
        "_poop_slice_from": _poop_slice_from,
    }
