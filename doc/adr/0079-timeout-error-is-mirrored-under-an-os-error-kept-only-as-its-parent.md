# 79. TimeoutError is mirrored under an OSError kept only as its parent

Date: 2026-11-27

## Status

Accepted

Amends [34. Only the exceptions POOP can reach are mirrored](0034-only-the-exceptions-poop-can-reach-are-mirrored.md)

## Context

ADR 34 mirrors the exceptions a program can reach, and leaves out the `OSError` subtree because a language with no files and no modules cannot reach it. `Async.timeout` changes that for one class. `asyncio.timeout` fails a body that outlasts it with `TimeoutError`, a program needs to name that class to catch it, and CPython's `TimeoutError` derives from `OSError`. Run on 3.15.2, its MRO is `TimeoutError`, `OSError`, `Exception`, `BaseException`.

Two trees were possible. `TimeoutError` could sit directly under `Exception`, which mirrors one class and departs from CPython's tree. Or `OSError` could be mirrored too, as the parent, which keeps the tree and puts in POOP a class that nothing else raises.

`OSError` adds five instance attributes to `BaseException`'s: `errno`, `strerror`, `filename`, `filename2` and `characters_written`.

## Decision

We will mirror `OSError` under `Exception` and `TimeoutError` under `OSError`, following CPython's tree. No other class of the `OSError` subtree is mirrored.

We will refuse the five attributes `OSError` adds, on the class and on the instance, as ADR 63 refuses `args`, `add_note` and `with_traceback`.

## Consequences

`except_(OSError, h)` catches a timeout, as `except OSError` does in Python, and `e.kind().name()` answers `TimeoutError`.

POOP holds an `OSError` that nothing in the language raises except through `TimeoutError`. `OSError.raise_("x")` works, as raising any mirror does.

Tests that used `OSError` as the example of an exception POOP withholds now use `PermissionError`.
