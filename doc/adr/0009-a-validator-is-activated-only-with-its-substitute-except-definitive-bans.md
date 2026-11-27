# 9. A validator is activated only with its substitute, except definitive bans

Date: 2026-04-22

## Status

Accepted

Amended by [75. Async def is a method and await is the message await_](0075-async-def-is-a-method-and-await-is-the-message-await.md)

## Context

A validator refuses a Python construct (ADR 6). Blocking without offering an alternative only breaks code without teaching anything.

Some constructs have no possible substitute inside POOP's model:

- `try/except*` used to name `Try(block).except_(ExcType, handler).run()` as its substitute, which was never true. `except*` splits an exception group among its handlers, and `except_` catches one exception whole. The honest fix would have been an `ExceptionGroup` mirror and a splitting `except_`. The rule that POOP mirrors the exceptions it can reach (ADR 34) says no. Groups come from `asyncio.TaskGroup` and from concurrency, and POOP has neither, so the only program that could meet one is a program that builds a group in order to raise it.
- `async def` / `await`: dropping the stdlib mirrors took `asyncio` with them, and `asyncio.run` was the only thing that could ever start a coroutine. That left `async def` as valid syntax nothing could execute.
- `open`: it was always listed as definitive on the grounds that POOP has no file-object abstraction, but it used to point at `Path.read_text()` / `write_text()` for the common cases. Dropping the `pathlib` mirror took that recipe with it, and POOP no longer touches the filesystem at all.
- `import`: POOP is the language, not the library. There is nothing from the stdlib to import, and an import would bind raw CPython values that answer to no POOP message; `from os import getcwd` would leak a raw Python callable returning a raw `str`.

## Decision

A validator is activated only when its substitute exists. A validator without an implemented substitute lives in an open change under `openspec/changes/` until the alternative is ready.

The exception is a definitive ban. A ban on a construct with no possible substitute inside POOP's model is activated without one. The definitive bans are `exec`/`eval`/`compile`, `exit`/`quit`, `breakpoint`, `globals`/`locals`/`vars`, `open`, `async def`/`await` and `try`/`except*`. For a definitive ban, the ban is the design decision, not a deferred item, and each is documented under its own validator. `import` is refused without a substitute on the same ground.

`try/except*` is refused with `try/except* is forbidden — nothing in POOP raises an exception group`.

## Consequences

- Every refusal outside the definitive bans names what to write instead.
- The async ban makes the refusal explicit and immediate, rather than letting a program define coroutines that silently never run. `no_async` needs a row for `ast.Await` because `ast.parse` accepts a module-level `await` and only `compile()` rejects it; without the row the node would surface as a raw CPython `SyntaxError`. `async with` and `async for` already belong to `no_with` and `no_loops`.
- `no_async` runs ahead of those validators in `DEFAULT_VALIDATORS`, so the root cause wins; both messages still surface under `--validators-only`, which collects every error. Async generators are also rejected by `no_yield`.
- A program's only channels are `"prompt".input()` and `Object.print()`. `input` keeps its substitute, symmetric to `Object.print()`; `EOFError` propagates raw and is catchable via `Try(lambda: prompt.input()).except_(EOFError, handler).run()`.
- The only names POOP injects, `Try` and `With`, are already in scope and need no import.
