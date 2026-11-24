# 67. Single-receiver `math` functions are messages of their type

Date: 2026-10-09

## Status

Accepted

## Context

POOP mirrors no module; `no_import`'s message is the sentence. `Int` already answered `ceil`, `floor`, `trunc` and `round`, the `math` functions CPython reaches through dunders, and `Float` answered `ceil`, `floor`, `trunc` and `is_integer`. The functions CPython does not reach through a dunder were not reachable at all.

Python 3.15 moved `isqrt`, `factorial`, `gcd`, `lcm`, `comb` and `perm` out of `math` into `math.integer` (PEP 791) *because* their only receiver is an integer, which is the argument for their being messages. Python 3.15 also added `isnormal`, `issubnormal` and `signbit` to the float predicates, beside the older `isnan`, `isinf` and `isfinite`. A receiver answering `isnormal` but not `isnan` would answer the rarer question and not the common one.

Smalltalk's integer set is four messages (`gcd:`, `lcm:`, `factorial`, `sqrtFloor`). CPython's is six, and `comb`/`perm` are integer arithmetic there.

## Decision

A function whose only receiver is one type is a message of that type, under CPython's name (ADR 8).

`Int` answers the `math.integer` six (`poop/types/int.py`): `isqrt`, `factorial`, `gcd`, `lcm`, `comb`, `perm`. All six rather than Smalltalk's four: the set is CPython's. Every edge follows CPython: `(12).gcd()` is 12 and `(4).gcd(6, 8)` is 2, as `math.gcd` takes any number of operands; `(2).comb(5)` is 0; `(5).perm()` is the factorial. The refusals are POOP's: a negative receiver answers `#isqrt needs a non-negative receiver, got -1`, where CPython says `isqrt() argument must be nonnegative` (the message as a call) or `n must be a non-negative integer` (an argument name the program never wrote), and a non-integer operand goes through `an_int`. `Boolean` delegates all six through `_as_int`, as it does the rest of the int side (ADR 47): `math.gcd(True, 2)` is 1.

`Float` answers the single-receiver predicates (`poop/types/float.py`): `isnan`, `isinf`, `isfinite`, `isnormal`, `issubnormal` and `signbit`. Every answer is `math`'s, as a `Boolean`: `(0.0).isnormal()` is `False`, `(5e-324).issubnormal()` is `True`, and `(-0.0).signbit()` is `True` where `(-0.0) < 0` is `False`.

## Consequences

- `fmax` and `fmin` are left out on purpose: they differ from the `max` and `min` `Float` already answers only in ignoring a NaN operand, and a second pair of names for a NaN edge is not a message a program reaches for.
- `Int` and `Boolean` do not answer the float predicates: for an integer every one of the six is a constant, and `math.isnan(3)` is CPython coercing rather than an integer behaviour.
- `Complex`'s predicates live in `cmath`; whether `Complex` answers them is a decision about `Complex`, not made here.
