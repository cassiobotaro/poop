# 21. `and_` and `or_` take blocks

Date: 2026-04-22

## Status

Accepted

## Context

`x and y` and `x or y` look like operators, so `no_and_or` (`poop/validators/no_and_or.py`) bans `ast.BoolOp` with `ast.And` and with `ast.Or`. The substitute has to keep what Python's `and`/`or` do: the right-hand side is evaluated only if it is needed.

## Decision

The substitutes are the messages `x.and_(lambda: y)` and `x.or_(lambda: y)`. Each receives a block rather than a value, so evaluation is lazy and the right-hand side runs only when the answer depends on it.

## Consequences

The short-circuit semantics of Python's `and`/`or` are preserved. Chained comparisons, which `no_and_or` does not inspect, are the one place an implicit `and` survives; ADR 27 records that exception.
