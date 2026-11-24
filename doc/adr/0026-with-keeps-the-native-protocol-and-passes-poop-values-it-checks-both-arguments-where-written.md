# 26. `With` keeps the native protocol and passes POOP values; it checks both arguments where written

Date: 2026-04-23

## Status

Accepted

## Context

`no_with` bans the `with` statement, and its substitute has to acquire and release a resource. POOP cannot redefine resource acquisition semantics without reimplementing every standard context manager (files, locks, etc.), which is impractical.

Using the native protocol leaked more than the protocol. `__exit__` used to receive `type(e)`, `e` and `e.__traceback__`: the native class rather than the mirror `except_` matches (and one no program can name), the bare exception rather than the `Error` a `Try` handler is given, and a traceback object, which is a whole introspection surface reached through a dunder `no_dunder_attribute` will not let a program spell. On the success path all three were Python's `None`, so `kind.is_none()`, the first thing an `__exit__` written in POOP asks, failed with `'NoneType' object has no attribute 'is_none'`.

Wrong arguments were reported late or in CPython's words:

- `With(5)` answered `'int' object is not callable`, one frame inside CPython's call machinery, true of every POOP object and silent about what was expected. `With(a_manager)` is the mistake worth optimizing for, because `With` takes a block that *answers* a manager, and passing the manager itself is the obvious first attempt.
- `With.do` left its body to the deferred call, which also answered `'int' object is not callable`, and answered it after `enter(cm)`, so the manager was acquired and released for a program that was never going to use it.
- `With` entered first and reached for the exit half only after the body had run, so a manager that could be entered but never exited ran its acquisition and then failed, with nothing left to undo the side effect.
- `With()` reached CPython's call machinery, as `Try()` did, and answered with a dunder and a phrase the wording sweep bans.

## Decision

`With(Object)` (`poop/types/with_.py`) implements the context manager protocol as a message-passing builder: `With(lambda: cm).do(lambda resource: body)`. It is exposed in `DEFAULT_NAMESPACE` through the `NAMESPACE` dict in `poop/transformers/with_.py`, with no AST rewrite.

- The manager block runs lazily, only when `.do()` is called. A `With` is single-use, as `Try` is. `.do()` releases its captured block once it runs, so a second `.do()` raises `RuntimeError` rather than re-running.
- `.do()` answers the body's value. When `__exit__` suppresses an exception the body produced no value, and `.do()` answers `none`.
- The manager implements Python's `__enter__`/`__exit__`, a deliberate primitive leak, consistent with `Try` using native exception types. A falsy `__exit__` answer re-raises the exception; a truthy one suppresses it.
- `__exit__` receives exactly what `Try` hands a handler: `poop_class_of(e)`, `Error(e)`, and `none` for the traceback POOP does not have and will not invent. The three-argument shape is unchanged.
- Each argument is checked where it was written. `__init__` refuses a non-block manager argument through `_require_block` (`poop/types/block.py`): `the manager argument must be a block, got a C — write With(lambda: …)`. `.do()` checks its body first, before the manager block runs.
- Both protocol slots are resolved before either is called, as Python's `with` does, and they are looked up on the type, where Python's protocol reads them. The refusal names the missing half (`it cannot be entered` / `it cannot be exited`) rather than the dunder CPython names.
- `With()` counts its argument in POOP's words: `With takes one block, got nothing — write With(lambda: …)`.

## Consequences

- A manager written to Python's signature still binds, and an `__exit__` written in POOP can ask its arguments messages on either path.
- A failure lands where the mistake was written, before a deferred block has had side effects.
- A `does_not_understand` hook answering a callable cannot forge a context manager.
- The two failing protocol programs are in the `test_no_python_wording` sweep, since a diagnostic spelling `__exit__` would name a construct `no_dunder_attribute` bans.
- The `__enter__`/`__exit__` protocol stays visible to anyone writing a manager.
