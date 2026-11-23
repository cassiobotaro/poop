# 32. Numeric equality follows CPython's numeric tower

Date: 2026-06-26

## Status

Accepted

## Context

POOP wraps each numeric type in its own class: `Int`, `Float`, `Complex` and `Boolean`. In CPython the numeric types compare by value across the tower, and `bool` is part of it because it is an `int` subclass. Across non-numeric types CPython answers false: an `int` is never equal to a `str`.

## Decision

POOP's numeric types compare by value across the tower exactly like CPython, in both directions: `Int(1) == Float(1.0)` is `true`, `Int(1) == Complex(1+0j)` is `true`, and `True == 1` is `true`. `Boolean` is part of the tower.

Comparison across non-numeric types stays `false`: an `Int` is never equal to a `Str`. Each `__eq__` returns `NotImplemented` for operands outside its numeric tower, so Python's reflected-comparison fallback applies.

## Consequences

- Equality between POOP numbers answers what the same comparison answers in Python.
- Because each `__eq__` defers to the reflected comparison for foreign operands, the relation stays symmetric.
