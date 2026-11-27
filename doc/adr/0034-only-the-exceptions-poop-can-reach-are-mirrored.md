# 34. Only the exceptions POOP can reach are mirrored

Date: 2026-07-15

## Status

Accepted

Amended by [79. TimeoutError is mirrored under an OSError kept only as its parent](0079-timeout-error-is-mirrored-under-an-os-error-kept-only-as-its-parent.md)

## Context

`Try.except_` and `raise_` need exception classes a program can name. Python 3.15 has 72 builtin exceptions; the one it added, `ImportCycleError`, sits under `ImportError`. A language with no files and no modules can never raise the `OSError` or `ImportError` subtrees.

- `RecursionError` is the most reachable of all, because recursion is POOP's substitute for every loop.
- Nothing in the language produces an `ExceptionGroup`, since there are no tasks and no `except*`. The catching construct Smalltalk calls an `ExceptionSet` is already what the tuple in `except_((ValueError, TypeError), h)` is.
- The reachability argument, checked against the surface, was one short. `Str.input` is the one message that reads from outside the program, and its one failure is end of input, reached by a pipe: `examples/basics/greet.py` answered `EOFError: EOF when reading a line`. Without a mirror the class could not be named (`except_(EOFError, …)` → `name 'EOFError' is not defined`), and `except_(Exception, …)` reported the kind as `Exception`.
- `encode`/`decode` can fail on the text they are given, which reaches the `Unicode*` family. Mirroring it would have meant reproducing a five-argument constructor whose `__str__` composes the `codec` sentence `_codec.py` exists to keep out. Unmirrored, `poop_class_of` answered the nearest mirrored ancestor, so a handler was told `ValueError` while the uncaught report printed `UnicodeEncodeError`. That was one failure under two names.

## Decision

POOP mirrors the exceptions it can reach, seventeen of them, in `poop/types/exceptions.py`: `Exception`, `ArithmeticError`, `LookupError`, `ZeroDivisionError`, `OverflowError`, `IndexError`, `KeyError`, `AttributeError`, `NameError`, `TypeError`, `ValueError`, `RuntimeError`, `NotImplementedError`, `RecursionError`, `AssertionError`, `StopIteration`, `EOFError`.

- `Try.except_(ValueError, h)` and `ValueError.raise_("msg")` take a POOP class.
- `input` raises the `EOFError` mirror with a sentence of its own: `there is no more input to read`.
- The `Unicode*` classes are not mirrored. `_codec.py` rewords both codec failures as a `ValueError`, which is what `UnicodeError` is in CPython's tree: `ascii cannot encode 'é' at position 1` / `utf-8 cannot decode byte 0xff at position 0`.
- `ExceptionGroup` is not mirrored.

## Consequences

- The substitutes for `try` and `raise` no longer take a raw primitive.
- The only I/O POOP has can be handled by name.
- A codec failure is reported under one class a program can spell, by a handler and by the uncaught report alike.
- With nothing to raise a group, `try/except*` is a definitive ban (ADR 9).
