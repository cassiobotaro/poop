# 70. `...` is a transformed literal, not a banned one

Date: 2026-07-15

## Status

Accepted

## Context

Every literal is transformed (ADR 2), `...` included: it becomes POOP's `Ellipsis`, a singleton like `none` (ADR 5).

POOP's own examples declare no abstract methods. The base class omits the message and lets polymorphism supply it.

## Decision

No validator bans `...`. With the literal transformed, `pass` and `...` are both valid stub bodies and neither leaks a primitive.

## Consequences

- `...` has no idiomatic role in POOP beyond Python muscle memory.
- A program that wants an abstract message omits it from the base class instead of writing a stub.
