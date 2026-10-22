# Proposal

## Why

Python 3.15 added `math.isnormal`, `math.issubnormal` and `math.signbit`,
three predicates whose only receiver is a float. `INFECTIONS.md` (the
`math.integer` paragraph) records that `Float` was left alone on purpose,
because taking them would "join a receiver that does not answer `isnan` or
`isinf` either, and that is a decision about `Float` and `math`". This
change takes that decision: `Float` answers the single-receiver `math`
predicates — the three 3.15 added and the three (`isnan`, `isinf`,
`isfinite`) that the same argument covers — the way `Int` answers the
`math.integer` six.

## What Changes

- **`Float` answers six predicates**, each a `Boolean`: `isnan()`,
  `isinf()`, `isfinite()`, `isnormal()`, `issubnormal()`, `signbit()`.
  Spelled as CPython spells them, as `isqrt` and `is_integer` each keep
  their own spelling. Every answer is `math`'s: `(0.0).isnormal()` is
  `False`, `(5e-324).issubnormal()` is `True`, `(-0.0).signbit()` is `True`.
- **`INFECTIONS.md`** replaces the "deliberately untouched" sentence with
  the decision and its reason, next to the `from_number` paragraph.

Out of scope, and why: `fmax` and `fmin`, which differ from the `max` and
`min` `Float` already answers only in ignoring a NaN operand — a second pair
of names for a NaN edge is not a message a program reaches for; `Int` and
`Boolean`, for which every predicate is a constant (`math.isnan(3)` is
CPython coercing, not an integer behaviour), and `Int.is_integer` is `int`'s
own method, a different precedent; `Complex`, whose predicates live in
`cmath` and are a decision about `Complex`; the two-operand and
float-answering `math` functions (`copysign`, `nextafter`, `ulp`, `fma`),
which are not predicates and were not what 3.15 added.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `float-type`: a `Float` answers `isnan`, `isinf`, `isfinite`, `isnormal`,
  `issubnormal` and `signbit` as a `Boolean` (ADDED requirements).

## Impact

- `poop/types/float.py`: six methods.
- `tests/test_types/test_float.py`: one test per predicate and edge.
- `INFECTIONS.md`: the `math.integer` paragraph's last sentence (line 1270)
  and a `Float` paragraph beside `from_number` (line 1282). `README.md`
  lists no per-type messages, so it does not change.
