# Design

## Context

See proposal.md — Why. `Float` (`poop/types/float.py`) already answers the
`math` functions CPython reaches through dunders (`ceil`, `floor`, `trunc`)
and its own `is_integer`; every one is a method answering a wrapper, and
`tests/test_cloak.py` sweeps for a public `property`. `Int` sets the
precedent for a `math` function becoming a message: `math.isqrt` on the
receiver's `_value`, CPython's name, the refusal reworded only where one
exists. The six predicates take no argument, so the only refusal they can
answer is the arity family's, which `message-arity` already owns.

## Goals / Non-Goals

**Goals:**
- Six zero-argument predicates on `Float`, each answering a `Boolean`
  through `to_boolean`, each delegating to the `math` function of the same
  name on `self._value`.

**Non-Goals:**
- Any new refusal or wording; nothing to refuse.
- Extending `Int`, `Boolean` or `Complex` (proposal — out of scope).

## Decisions

- **CPython's spelling.** `isnan`, not `is_nan`: the rule is to follow
  CPython's name for a mirrored operation, and `Float.is_integer` keeps
  `float.is_integer`'s underscore for the same reason `Int.isqrt` keeps
  `math.isqrt`'s absence of one. Alternative: a POOP spelling (`is_nan`)
  matching Smalltalk's `isNaN`; rejected because the name a reader will try
  first is the one CPython taught them.
- **All six, not only 3.15's three.** `INFECTIONS.md` names `isnan` and
  `isinf` as the same decision; taking `isnormal` without `isnan` would
  leave the receiver answering the rarer question and not the common one.
- **A `Boolean`, not a `bool`.** `to_boolean`, as `is_integer` does; a
  predicate's answer is a POOP value a program can send `if_true` to.

## Risks / Trade-offs

- [`Float._value` may hold an `int` (the slot admits it, per the `hex`
  comment)] → every `math` predicate accepts an `int`, so no `float(...)`
  cast is needed; a test with `Float(3)` guards the path if the constructor
  admits it.
- [Test sweeps] → `tests/test_cloak.py` and the wording sweeps run in the
  integration task; six plain methods introduce no property and no sentence.
