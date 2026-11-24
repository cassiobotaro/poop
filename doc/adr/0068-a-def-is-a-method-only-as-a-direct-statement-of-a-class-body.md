# 68. A `def` is a method only as a direct statement of a class body

Date: 2026-07-17

## Status

Accepted

## Context

`no_free_functions` refuses a function that is not a message to any object (ADR 6). It used to count class *nesting*, and that was not enough: a `def` nested inside a method sits at `class_depth > 0` yet its parent is the method, not the class, so it slipped through as a receiver-less named local function.

Smalltalk has blocks, not named local functions.

## Decision

A function is a method only when it is a direct statement of a class body. The validator registers each `ClassDef`'s direct-body `def`s as methods and rejects every other `FunctionDef`/`AsyncFunctionDef`, module level and method-nested alike.

## Consequences

- A local helper inside a method is written as a lambda: it is the sanctioned receiver-less callable, invoked as `block()` (ADR 28).
- The rule no longer depends on how deep a `def` sits, only on what its parent is.
