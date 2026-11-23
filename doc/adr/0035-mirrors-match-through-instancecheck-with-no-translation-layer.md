# 35. Mirrors match through `__instancecheck__`, with no translation layer

Date: 2026-07-15

## Status

Accepted

## Context

POOP mirrors the exceptions a program can reach (ADR 34), so that `Try.except_(ValueError, h)` and `ValueError.raise_("msg")` take a POOP class instead of a raw primitive. A POOP class must then match the native exception CPython raises, its twin, without a layer that converts one into the other.

The handler is POOP's own code. `Try._execute()` catches `except BaseException` and then matches with `isinstance()`; no Python `except` clause ever does the matching. That is what makes mirroring affordable: a metaclass `__instancecheck__` is enough for a POOP class to match its native twin.

Two failure modes constrain how the twin is found:

- If the native class were inherited, a user's `class MyError(Exception)` would inherit the root's `_native = Exception` and catch every exception in the program, silently and totally. The obvious alternative, an `__init_subclass__` setting `_native = cls`, recurses forever.
- Before the root inherited `Object`, `class MyError(Exception)` sat outside the Object tree entirely.

## Decision

POOP matches a mirror against a native exception through the metaclass `__instancecheck__` of `PoopExcMeta` (`poop/types/exceptions.py`). There is no translation layer.

- Each mirror subclasses its native twin, so it stays raisable.
- `_native` is read from the class's own `__dict__` and never inherited.
- The root mirror also inherits `Object`, so a user exception lands inside the Object tree and answers `print()` and `class_name()`.

`raise_` is a class-side message on `PoopExcMeta` rather than a parse-time rewrite; ADR 49 records that.

## Consequences

- A handler written against a mirror catches the native CPython raises, and code that caught the native still catches a mirror, because the mirror is a subclass of it.
- A program's own exception class catches only itself and its subclasses, never every exception.
- A user exception is an ordinary POOP object on the class side.
- Code that must tell a native apart from its mirror has to test `type(exc)`, because `isinstance` matches both on purpose. The rewording of a mutation-during-iteration `RuntimeError` tests it this way, so that only a native one is reworded.
