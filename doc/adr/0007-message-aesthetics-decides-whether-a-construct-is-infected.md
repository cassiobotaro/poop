# 7. Message aesthetics decides whether a construct is infected

Date: 2026-04-22

## Status

Accepted

## Context

ADR 6 makes every operation a message, which leaves open how to judge a given Python construct. One test is "does it exist in Smalltalk?". That test does not catch operators and free functions that call methods internally: `-x`, `not x`, `~x`, `len(x)` and `abs(x)` all end in a method call, yet they read as procedure.

## Decision

The central criterion of an infection is "does it look like an object receiving a message?", not "does it exist in Smalltalk?". POOP code must look like a conversation between objects, not a sequence of operations.

A construct with a procedural look is replaced even when it calls a method internally: `-x` by `x.negated()`, `not x` by `x.not_()`, `~x` by `x.bit_invert()`, `len(x)` by `x.len()`, `abs(x)` by `x.abs()`.

## Consequences

- A construct is judged by how it reads: unary operators and free functions such as `len` and `abs` are refused even though they call methods internally.
- Binary operators are judged by the same criterion in ADR 27.
