# 61. The recursion limit is sized by frames per send

Date: 2026-10-09

## Status

Accepted

## Context

Recursion is POOP's substitute for every loop, which makes `RecursionError` the most reachable exception in the language. The budget it runs against is also POOP's to set.

One POOP message send is six Python frames: `Block.__call__`, `_MethodBlock.__call__` twice, the branch method, and the reader's own method and block. Under CPython's default limit of 1000, a self-sending message ran 164 levels deep where the same recursion written as a Python function ran 998.

Two of the six frames are `_MethodBlock.__call__`, the price of a method read off an object being a block (ADR 41). Bypassing that wrap and re-measuring the same program gives 247 levels instead of 164, so that feature costs a third of the ceiling.

Raising the limit is safe rather than a gamble because CPython 3.15 guards the C stack separately and answers a catchable `RecursionError` (`Stack overflow (used 8148 kB) while calling a Python object`) instead of crashing.

## Decision

`poop/executor.py` sizes the recursion limit from the frame cost of a send: `1000 * _FRAMES_PER_SEND`. That buys a POOP program roughly the thousand levels a Python program already gets.

## Consequences

`tests/test_recursion.py` asserts both the depth and the C-stack floor.

The limit concerns *structural* recursion, a tree walk whose depth follows the data. `while_true` and `while_false` are real Python `while` loops and have no ceiling at all.

The cost of the method-block wrap, a third of the ceiling, is recorded next to the limit.
