from operator import index as _index
from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.int import Int
from poop.types.range import Range

if TYPE_CHECKING:
    from poop.types._index import Index


def _poop_range(*args: object, **kwargs: object) -> Range:
    """`range(stop)` / `range(start, stop[, step])`, read by index.

    `_index`, not `int`: `Range.__init__` already takes the index rung of the
    tower for this reason, and the converter in front of it read `int(...)`
    instead — which *truncates* where `index` refuses, so `range(3.5)` answered
    `range(0, 3)` and `range(1, 10, 2.0)` a step of 2, silently running over a
    different sequence than the program describes. It also refused the
    non-numeric cases in `int`'s vocabulary (`int() argument must be a string,
    a bytes-like object or a real number`), naming a call for something the
    program spelt `range`. `index` answers `'float' object cannot be
    interpreted as an integer`, which is CPython's own and, through the cloak,
    names the wrapper by the builtin it stands for. The boolean rung still
    passes, since admitting it is exactly what `index` is for.
    """
    refuse_extra_arguments(
        "range",
        args,
        kwargs,
        most=3,
        built_from="a stop, or a start and a stop and an optional step",
        hint="write range(stop) or range(start, stop, step)",
        empty=False,
    )
    # `*args: object` is what the guard above needs to count; `_index` refuses
    # anything outside the index rung at runtime, which is the check that
    # matters and the one this converter exists for.
    values = [_index(cast("Index", arg)) for arg in args]
    # CPython's three shapes, normalised to (start, stop, step) once: `Range`
    # takes an inclusive stop, so the exclusive one moves back one step's
    # sign — the arithmetic `Range._from_native` states. A zero step keeps
    # its sign as `-1` here and is refused where every zero step is, in
    # `Range.__init__`, with POOP's sentence rather than CPython's
    # `range() arg 3 must not be zero`.
    match values:
        case [stop]:
            start, step = 0, 1
        case [start, stop]:
            step = 1
        case [start, stop, step]:
            pass
    sign = 1 if step > 0 else -1
    return Range(Int(start), Int(stop - sign), Int(step))


class _RangeRewriter(BuiltinRewriter):
    builtin = "range"
    call_target = "_poop_range"
    name_target = "_poop_range_cls"


class RangeTransformer(BaseTransformer):
    rewriter = _RangeRewriter
    BINDINGS = {
        "_poop_range": _poop_range,
        "_poop_range_cls": builtin_alias(Range, _poop_range, "range"),
    }
