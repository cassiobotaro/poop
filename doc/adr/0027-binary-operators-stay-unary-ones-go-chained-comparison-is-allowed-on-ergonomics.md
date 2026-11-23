# 27. Binary operators stay, unary ones go; chained comparison is allowed on ergonomics

Date: 2026-04-23

## Status

Accepted

## Context

ADR 7 decides an infection by whether a construct looks like an object receiving a message. Operators were considered for blocking.

- Binary operators mirror Smalltalk, where binary messages (`+`, `-`, `*`, …) are the idiomatic way to express arithmetic and comparison. Blocking them would force `a.add(b)`, `a.lt(b)` and so on, more verbose without being more expressive or principled.
- Unary operators differ: `-a` (`USub`) and `~a` (`Invert`) have named message equivalents (`a.negated()`, `a.bit_invert()`) and carry no ergonomic benefit in infix form.
- `x += 1` is syntactic sugar for `x = x + 1`. Both rebind the variable with the same arithmetic operation, there is no more idiomatic message-passing substitute, and blocking `+=` would be a purely cosmetic restriction.

Chained comparison needed its own argument. `no_and_or` inspects only `ast.BoolOp`, so `1 < 2 < 3`, a single `ast.Compare` with several comparators that Python evaluates as `(1 < 2) and (2 < 3)` with short-circuit, carries no `and` token and is never seen. Unlike the other allowed constructs it has a substitute, `(1 < x).and_(lambda: x < 10)`. Smalltalk cannot express the form at all: `1 < x < 10` parses as `(1 < x) < 10`, since binary messages are strictly left-to-right, and sends `#<` to a Boolean, which answers `doesNotUnderstand:`. On the other side, `a < b < c` expands to `(a < b) and (b < c)`, whose conjuncts share the middle operand, so no arbitrary `P and Q` is reachable this way: the construct is a range check, not a general `and` escape hatch. Running both confirmed the asymmetry: `1 < x < 10` answers `True` while `(1 < x) and (x < 10)` answers `and operator is forbidden — use .and_(lambda: ...) instead`, and a `Probe` whose `__lt__` prints, evaluated as `p < p < p`, prints once. The question was raised twice and settled the same way both times.

## Decision

POOP allows the binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`), which are `ast.BinOp` and `ast.Compare` nodes, and augmented assignment: `ast.AugAssign` is intentionally not blocked.

POOP blocks the unary operators that have a named message equivalent: `-a` is written `a.negated()` and `~a` is written `a.bit_invert()`.

POOP allows chained comparison under the binary allowance, deliberately. It is the single place an implicit `and` survives in POOP. A program that wants it spelled out decomposes it: `(a < b).and_(lambda: b < c)`.

## Consequences

- Arithmetic and comparison keep their infix spelling, and every range check keeps its Python-obvious one.
- A chain keeps Python's short-circuit semantics without routing through a block.
- Chained comparison is the sole allowance resting on Python ergonomics rather than on the absence of a substitute. The opposite call was made for raw dunder access (ADR 33): `xs.__len__()` also has a substitute, but unlike a chain it leaks a raw Python primitive as well, so ergonomics had nothing to weigh against.
