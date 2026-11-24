# 69. A constructor call is read by its converter at run time

Date: 2026-10-14

## Status

Accepted

## Context

A rewriter sees the expressions a call wrote, not the values it will receive. Two constructors used to fold their arguments at parse time, and both folds were wrong for some calls:

- `slice`: CPython's one-argument rule, `slice(stop)` is `slice(None, stop, None)`, was applied by the rewriter on the expressions written. A starred argument is one expression carrying any number of values, so `slice(*xs)` with `xs = (1, 5)` was folded into `slice(None, 1, 5)`.
- `dict`: the parse-time fold of `dict(a, k=v, **b)` accepted `dict(**{1: 2})` and `dict(a, x=1, **{"x": 2})`, both of which CPython refuses.

## Decision

A constructor call is read by its converter, on the values the call received, never folded by the rewriter (ADR 53 sends every call to the converter).

`slice`'s one-argument rule is applied by the converter. `dict(a, k=v, **b)` is not folded: a `**` splat at a call site is unwrapped by `VarargsTransformer` for every call alike, so the call answers what any call answers: `keywords must be strings` for `dict(**{1: 2})`, `dict() got multiple values for keyword argument 'x'` for `dict(a, x=1, **{"x": 2})`.

## Consequences

- A starred or double-starred argument means the same thing in a constructor call as in any other call.
- `obj.slice(s, stop)`, a `Slice` followed by a bound, is refused with `#slice takes a slice or bounds, not both — write .slice(slice(1, 3)) or .slice(1, 3)` rather than answering the slice and dropping the bound in silence.
