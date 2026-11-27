# 78. A program's builtins hold __import__ for CPython's own imports

Date: 2026-11-27

## Status

Accepted

Amends [40. Programs are confined to a builtins allow-list](0040-programs-are-confined-to-a-builtins-allow-list.md)

Amends [76. An async method answers a coroutine wrapped where the class is built](0076-an-async-method-answers-a-coroutine-wrapped-where-the-class-is-built.md)

## Context

CPython warns when a coroutine is collected without being awaited. To emit the warning it imports through the builtins of the frame the coroutine is collected in, and for a program's coroutine that frame is the program's. ADR 40 confines a program to an allow-list that held no `__import__`, so CPython printed `KeyError: '__import__'` where the warning belonged.

ADR 76 answered that by emitting the warning from `Coroutine.__del__`. That covered a coroutine dropped on its own. It did not cover one held in a reference cycle, such as the traceback of a refused send, which the collector can finalize before the `Coroutine` around it, and CPython's own attempt then failed the same way. The emitted warning also differed from CPython's: it pointed at the method's `def` line rather than the line that dropped the coroutine, and it lacked the tracemalloc hint.

The requirement is that the warning behave as CPython's does.

No program can spell `__import__`. `no_import` refuses the `import` statement, `no_dunder_name` refuses the bare name, and ADR 33 refuses a dunder read at runtime, `get_attr` included.

## Decision

We will put `builtins.__import__` in `_ALLOWED_BUILTINS`, as machinery CPython calls from a program's frame, alongside `__build_class__`.

We will remove `Coroutine.__del__`. CPython emits the "never awaited" warning itself, in every case, with its own text and location.

## Consequences

A coroutine never awaited warns exactly as it does in CPython, including when the collector finalizes it from a cycle.

The allow-list is no longer only names a program may write. `__import__` is the first entry a program cannot reach by any spelling, and the comment above `_ALLOWED_BUILTINS` says why it is there.

Code that builds an `Interpreter` with no validators, through the Python API, can now run `import`. That was already true of every other construct the validators refuse.
