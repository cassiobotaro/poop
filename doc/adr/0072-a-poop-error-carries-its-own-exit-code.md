# 72. A POOP error carries its own exit code

Date: 2026-11-27

## Status

Accepted

## Context

`poop` exits 1 when the source cannot be read, 2 on a parse or usage error, 3 when validation fails and 4 when the program fails at run time. The CLI looked these codes up in a dict keyed by the exact class of the error, `EXIT_CODES[type(exc)]`. A subclass of any of the four error classes was missing from that dict, so the handler that turns a failure into a clean exit would raise `KeyError` itself. The codes were bare integers, and their meaning was written in a comment above the dict.

## Decision

We will declare the exit code on the error class, as `exit_code: ClassVar[ExitCode]`, and the CLI will read `exc.exit_code`. A subclass inherits its parent's code. `PoopError` itself declares `FAILED`, so an error with no code of its own still exits as a failure.

The codes are an `IntEnum`, `ExitCode`, defined in `poop/errors.py` beside the classes that use it. Each member is named for what the code tells a script: `UNREADABLE`, `NOT_A_PROGRAM` for a parse error and a usage error alike, `REFUSED` and `FAILED`. A member is not named after the class that raises it.

## Consequences

A new error class has an exit code without registering one anywhere, and a script branching on the codes sees no change.

`poop/errors.py` now knows about process exit codes, which only the CLI uses. The REPL reads the same classes and ignores the attribute.

There is no member for 0, because success raises nothing and `typer.Exit()` exits 0 by default.
