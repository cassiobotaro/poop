import ast
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types.exceptions import MIRRORS
from poop.types.slice import Slice

if TYPE_CHECKING:
    from poop.types._index import Index
    from poop.types.none import NoneClass


def _poop_slice_from(*args: object, **kwargs: object) -> Slice:
    """`slice(...)`, guarded. Proposal 9 recorded that `Slice(...)` *is* the
    call, so unlike its siblings this one had no factory at all — and the
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
    )
    if not args:
        raise MIRRORS["TypeError"](
            "slice is built from a stop, or a start and a stop and an optional "
            "step, got nothing — write slice(stop) or slice(start, stop, step)"
        )
    return Slice(*cast("tuple[Index | NoneClass | None, ...]", args))


class _SliceRewriter(BuiltinRewriter):
    builtin = "slice"
    call_target = "_poop_slice_from"
    name_target = "_poop_slice"

    def call_args(self, node: ast.Call) -> list[ast.expr]:
        args = super().call_args(node)
        # CPython's one-argument `slice(stop)` means `slice(None, stop, None)` —
        # the lone argument is the stop, not the start. Slice(...) binds
        # positionals as (start, stop, step), so a bare `slice(x)` would wrongly
        # make x the start; inject the implicit None start to mirror the builtin
        # (NoneTransformer has already run, so a raw `None` constant reaches
        # Slice, whose _coerce maps it to None).
        if len(args) == 1 and not node.keywords:
            args.insert(0, ast.Constant(value=None))
        return args


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_slice": Slice,
        "_poop_slice_from": _poop_slice_from,
    }
