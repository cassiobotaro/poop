# 81. CancelledError is mirrored as a second root

Date: 2026-11-27

## Status

Accepted

Amends [34. Only the exceptions POOP can reach are mirrored](0034-only-the-exceptions-poop-can-reach-are-mirrored.md)

## Context

`Async.timeout` cancels a body that outlasts its delay, and `asyncio` turns that cancellation into `TimeoutError` with `raise TimeoutError from exc`. The `CancelledError` never reaches a handler as the failure itself, but it is the timeout's cause. The uncaught report lists the cause, and a handler reads it with `e.cause()`.

Unmirrored, `CancelledError` answered for itself through the nearest mirrored ancestor, which `poop_class_of` falls back to `Exception`. The report read `caused by Exception`, where CPython names `CancelledError`, and `e.cause().kind().name()` answered `Exception` for a class that does not derive from it. CPython derives `CancelledError` from `BaseException`, so that `except Exception` does not catch a cancellation.

Every mirror so far descended from the `Exception` mirror, the single root. A root mirror carries the instance side (`message`, `kind`, `raise_` and the rest), and `cloak` renames a class's own functions in place.

## Decision

We will mirror `CancelledError` as a second root: built on the native `CancelledError` and `Object`, with no POOP parent, as the `Exception` mirror is built on the native `Exception` and `Object`.

Each root gets its own copies of the instance-side functions, so that cloaking one root does not rename the other's.

## Consequences

The uncaught report of an expired timeout reads `caused by CancelledError`, as CPython's does, and `e.cause().kind().name()` answers `CancelledError`.

`except_(Exception, h)` does not catch a cancellation, and `CancelledError.is_subclass(Exception)` answers `False`, both as in CPython.

A program can name `CancelledError` and write `except_(CancelledError, h)`. Inside a timeout's body, a handler that swallows the cancellation keeps the timeout from raising `TimeoutError`, which is what CPython does with the same handler.

`poop/types/exceptions.py` imports `asyncio` to reach the native class. `poop` already imported it for `Async`.
