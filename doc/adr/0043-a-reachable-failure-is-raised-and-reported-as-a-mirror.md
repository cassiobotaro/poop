# 43. A reachable failure is raised and reported as a mirror

Date: 2026-07-27

## Status

Accepted

## Context

POOP mirrors the exceptions a program can reach (ADR 34), and a mirror matches its native twin (ADR 35). Two paths still put a class a program cannot spell in front of the reader.

A wrapper composing a POOP message used to carry it on a native class. That labelled POOP's advice with Python's vocabulary, and nothing stopped the next wrapper from doing the same.

The uncaught report read `type(exc).__name__` in `_describe` (`poop/executor.py`), so every unknown selector in the language, the most-printed diagnostic there is, reported `MessageNotUnderstood`. That is POOP's own class and is outside `MIRRORS`, so it is unspellable (`NameError: name 'MessageNotUnderstood' is not defined`), while `except_(AttributeError, …)` caught it and `e.class_().name()` answered `AttributeError`. One failure had two names, a disagreement already closed for the `Unicode*` family.

## Decision

Inside `poop/types/` and `poop/transformers/`, a failure a program can reach is raised as a mirror, `mirrors.TypeError(...)`, and never as the bare builtin. `poop/types/mirrors.py` binds each mirror under its own name once `exceptions` has built the table, so a raise reads as a raise rather than as a string key into a registry.

The uncaught report names the class through `poop_class_of`, so the class it prints is one `except_` can be handed.

Two spellings stay native, both exempt by rule rather than by site:

- `__getattr__`'s dunder refusal, which is Python's attribute protocol answering Python's own probe, and is reached while `exceptions` is still importing (the mirrors are built on `Object`);
- the abstract-stub and import-time guards no program can reach.

## Consequences

- Because the mirrors subclass their twin, the change is invisible at runtime: anything that caught the native still catches it. It is a guardrail for the wording work, not a behaviour change.
- A program can catch, by name, every class the uncaught report shows.
- `tests/test_mirrored_raises.py` sweeps both packages for a native raise, since per-site tests cannot stop the next wrapper from reintroducing one.
- `tests/test_no_python_wording.py` sweeps the failing programs for the invariant that the class in an uncaught report is one `except_` can be handed.
