from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types._argument import an_int
from poop.types.int import Int
from poop.types.range import Range


def _poop_range(*args: object, **kwargs: object) -> Range:
    """`range(stop)` / `range(start, stop[, step])`, read by index.

    `an_int`, not `int`: the converter once read `int(...)`, which *truncates*
    where an index refuses, so `range(3.5)` answered `range(0, 3)` and
    `range(1, 10, 2.0)` a step of 2 — silently running over a different
    sequence than the program describes. It then read `operator.index` and
    kept CPython's `'float' object cannot be interpreted as an integer`, the
    very sentence `an_int` replaced on every other integer argument in the
    language; now each argument is refused by its role (`#range's stop must
    be an int, got a str`). The boolean rung still passes, since admitting it
    is exactly what an index is for.
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
    # The role each position plays, so a refusal names it as CPython's own
    # signature does: a lone argument is the stop.
    roles = ("stop",) if len(args) == 1 else ("start", "stop", "step")
    values = [
        an_int(arg, "range", role) for arg, role in zip(args, roles, strict=False)
    ]
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
