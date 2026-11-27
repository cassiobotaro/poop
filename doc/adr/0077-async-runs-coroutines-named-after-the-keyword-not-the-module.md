# 77. Async runs coroutines, named after the keyword, not the module

Date: 2026-11-27

## Status

Accepted

## Context

An async method needs something that starts a coroutine, and that thing has to be a name a program can reach. `DEFAULT_NAMESPACE` holds two user-facing names, `Try` and `With`. Each is the PascalCase spelling of the keyword it replaces, and neither needs an import.

POOP is the language, not the library. The stdlib mirrors were dropped, and ADR 9 refuses `import` on that ground. `asyncio` is a module with dozens of functions.

Python's own name for the runner, `asyncio.run`, is the one a reader coming from Python looks for.

`asyncio.create_task` and `asyncio.TaskGroup` hand a program a task to hold and cancel. `TaskGroup` raises an `ExceptionGroup`, and ADR 9 refuses `except*` because nothing in POOP raises one.

## Decision

We will inject one class, `Async`, named after the keyword `async` as `Try` and `With` are named after theirs. It has no instances, and its messages are `staticmethod`s read off the class: `Async.run(coroutine)`, `Async.sleep(delay, result=none)` and `Async.gather(*coroutines)`. Each checks its arguments' kinds in POOP's words when it is sent, and each answers POOP values: `gather` answers a `List`, and `sleep` answers `none` unless given a result.

We will expose no tasks, no cancellation and no `TaskGroup`.

## Consequences

`DEFAULT_NAMESPACE` holds three user-facing names. `no_namespace_shadow` protects `Async` with no change, since its protected set is derived from the namespace.

`Async` does not read as a mirror of `asyncio`, and a program finds its whole surface in three messages. A reader who looks for `asyncio.run` finds it through `MIGRATION.md`.

A lowercase typo, `async.run(x)`, fails in CPython's parser before any validator runs, since `async` is a keyword. The same typo against `asyncio` would have been a `NameError`, which POOP already words with a hint.

Without tasks, a program cannot start a coroutine and leave it running. Concurrency happens inside `gather` and ends when the gather is awaited.
