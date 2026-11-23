# 65. The uncaught report shows the chain, nearest first, by CPython's rule

Date: 2026-10-19

## Status

Accepted

## Context

The uncaught report used to print the last exception alone. A failure raised inside a `Try` handler hid the one it was handling, and `raise_from`, whose whole point is the cause, would have changed nothing a reader sees.

POOP's report opens with the final exception, and the quoted source line is its line; only it has a location.

Every sentence POOP composes is raised `from None` over CPython's native exception, so CPython's own wording is suppressed and does not come back through the chain: `[1].at(5)` reports its own sentence and nothing under it.

## Decision

Under the `poop: <Kind>: <message>` line and its source line, the report (`poop/types/exceptions.py`, `poop/errors.py`) gives each link of the chain one line:

- `caused by <Kind>: <message>` for an explicit cause;
- otherwise `while handling <Kind>: <message>` for a context that was not suppressed.

The chain ends at a suppressed link or at an exception already listed, since a handler can link two to each other. The order is the reverse of CPython's, nearest first, because the report opens with the final exception.

`Error.context()` answers by the same rule, so a handler and the terminal see one chain. The CLI and the REPL share the renderer and both show it.

## Consequences

A failure inside a handler shows the one it was handling, and `raise_from`'s cause is visible.

A sentence POOP composes shows nothing under it, because it is raised `from None`.
