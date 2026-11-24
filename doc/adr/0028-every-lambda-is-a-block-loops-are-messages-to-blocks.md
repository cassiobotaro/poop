# 28. Every `lambda` is a `Block`; loops are messages to blocks

Date: 2026-04-26

## Status

Accepted

## Context

In Smalltalk, `[...]` syntax creates a block. Python has no block literal syntax. `lambda`, a deferred expression, is the closest equivalent.

A loop also needs a receiver. On `Boolean`, `while_true` and `while_false` would carry the philosophical problem of a receiver that is irrelevant to the message.

## Decision

`Block` (`poop/types/block.py`) is a first-class object wrapping a callable. The block transformer (`poop/transformers/block.py`) intercepts every `ast.Lambda` and rewrites it to `Block(lambda: ...)`, so `lambda` is the block literal and the programmer never names `Block`.

`while_true` and `while_false` live on `Block`, not on `Boolean`. The receiver is the condition block, the object whose value determines whether the loop continues. This matches Smalltalk's `[cond] whileTrue: [body]`:

- `[cond] whileTrue: [body]` is `(lambda: cond).while_true(lambda: body)`;
- `[cond] whileFalse: [body]` is `(lambda: cond).while_false(lambda: body)`;
- `[block] value` is `(lambda: expr)()`;
- `[block] value: arg` is `(lambda x: expr)(arg)`.

## Consequences

- Programmers write plain lambdas and get POOP block objects that answer messages.
- The `Block(...)` wrapper is transparent; no program spells it.
- A loop reads as a message to its condition block, as in Smalltalk.
