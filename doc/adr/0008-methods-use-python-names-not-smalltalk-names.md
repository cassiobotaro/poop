# 8. Methods use Python names, not Smalltalk names

Date: 2026-04-22

## Status

Accepted

## Context

POOP takes its model from Smalltalk, and Smalltalk has its own names for the collection API: `collect`, `select`, `reject`, `detect`, `do:`, `inject:into:`. A POOP program is written by a reader who knows Python's names for the same operations.

Iteration has no usable Python name. `for` is a Python keyword, and `for_each` is a Java/JS idiom with no Python equivalent. Folding does have one: `functools.reduce` is the Python name for Smalltalk's `inject:into:`.

The `2026-10-22-float-answers-315-math` change applied the rule to `math` predicates on `Float`. It considered a POOP spelling (`is_nan`) matching Smalltalk's `isNaN`, and rejected it because the name a reader will try first is the one CPython taught them.

## Decision

All methods follow the corresponding Python name: builtins, dunders and collection API. `map`, not `collect`; `filter`, not `select`; `filter_false`, not `reject`; `find`, not `detect`. Smalltalk names are not implemented.

The exception is iteration, which uses `do` (from Smalltalk `do:`) instead of `for_each`. `do` is the canonical Smalltalk message for iteration and reads as a message to an object. It returns `none`, like a `for` loop.

Folds use `reduce(init, block)`, named after `functools.reduce`.

A message that mirrors a CPython function keeps CPython's exact spelling, underscores or not: `Float.isnan`, not `is_nan`, as `Int.isqrt` keeps `math.isqrt`'s spelling and `Float.is_integer` keeps `float.is_integer`'s.

## Consequences

- A reader who knows Python finds a message under the name they already try.
- `do` is the one Smalltalk name in the API.
- Dunders exposed as plain methods take their Python names too (ADR 13).
