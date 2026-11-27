# Proposal

## Why

After `async-methods`, an async method can await, but nothing around the
await can guard it. `Try(...).run()` and `With(...).do(...)` run their block
at once, and a block only creates the coroutine: the failure is raised later,
at `.await_()`, outside the `Try`, and the body of a `With` runs after its
manager has already exited. Run on 3.15.2, a `ValueError` raised by an
awaited coroutine escaped a `try` around the block that created it. Without
this change, a program can only catch an asynchronous failure by wrapping
the whole `Async.run`, and `Async.timeout`, the deadline every network-shaped
program wants, would be uncatchable where it fires.

## What Changes

- **New injected name `AsyncWith`**, the pair of `With` for an asynchronous
  context manager: `AsyncWith(lambda: cm()).do(lambda resource: coroutine)`
  answers a coroutine; awaiting it enters the manager, awaits the body's
  coroutine inside it, and exits. The body must answer a coroutine.
- **An awaited `Try`.** `Try(lambda: coroutine).except_(...).else_(...)`
  answers `.await_()`: it awaits the block's coroutine inside the guard and
  applies the handlers. A handler or `else_` may answer a value or a
  coroutine, which is awaited.
- **The synchronous forms refuse a coroutine.** `Try.run()`, `Try.finally_()`
  and `With.do()` refuse a block or body that answers a coroutine, naming
  the asynchronous form, instead of letting the failure or the body escape
  the guard in silence.
- **`Async.timeout(delay)`** answers a `Timeout`, an asynchronous context
  manager that fails the body with `TimeoutError` once `delay` seconds pass.
  The body receives the `Timeout`, which answers `expired()`.
- **`TimeoutError` and `OSError` are mirrored**, `TimeoutError` under
  `OSError` as in CPython's tree. `OSError` is mirrored only as its parent.
- **`no_with` names `AsyncWith`** as the substitute for `async with`.
- **Two ADRs**: the asynchronous forms defer their run to the await and the
  synchronous ones refuse a coroutine (extending ADRs 26 and 54); and
  `TimeoutError` is mirrored under an `OSError` that exists only as its
  parent (extending ADR 34).
- **Docs**: `AGENTS.md` (four user-facing names), `README.md`,
  `MIGRATION.md`, and a new example.

## Capabilities

### New Capabilities
- `async-with-type`: `AsyncWith`, how it is built, awaited and refused.
- `timeout-type`: the `Timeout` that `Async.timeout` answers.

### Modified Capabilities
- `async-type`: gains `Async.timeout`; the instance refusal names it.
- `try-type`: an awaited `Try`, and `run`/`finally_` refusing a coroutine.
- `with-type`: `do` refuses a body that answers a coroutine.
- `exception-mirrors`: `TimeoutError` and `OSError` are reachable and caught
  as CPython's tree says.
- `no-with-validator`: `async with` names `AsyncWith`.

`async-type` and `no-with-validator` are created by `async-methods`, which
is archived first.

## Impact

- New: `poop/types/async_with.py`, `poop/types/timeout.py`,
  `poop/transformers/async_with.py`, two ADRs, one example.
- Edited: `poop/types/try_.py`, `poop/types/with_.py` (the protocol lookup
  shared with `AsyncWith`), `poop/types/async_.py`,
  `poop/types/exceptions.py`, `poop/types/mirrors.py`,
  `poop/transformers/_registry.py`, `poop/validators/no_with.py`, and their
  tests.
- `DEFAULT_NAMESPACE` grows to four user-facing names.
- No program that runs today changes behaviour: no coroutine can exist
  before `async-methods`, so the new refusals in `Try` and `With` cannot
  fire on an existing program.

## Out of scope

- **`Timeout.when()` and `Timeout.reschedule()`.** Both take or answer an
  instant on the event loop's clock, which POOP does not expose, so neither
  would have a use. `expired()` is the one question a program can act on.
- **A cleanup clause on an awaited `Try`.** `finally_` runs the `Try` at
  once, by its current contract. An asynchronous cleanup is what `AsyncWith`
  is for.
- **A synchronous manager around an awaiting body**, which Python allows as
  `with lock: await x`. `With` refuses such a body and names `AsyncWith`; a
  program gives its manager `__aenter__`/`__aexit__` instead.
- **`CancelledError`.** `Async.timeout` converts the cancellation it causes
  into `TimeoutError` before a program sees it, and no other path to cancel
  a coroutine is reachable.
- **The rest of the `OSError` subtree.** POOP has no I/O; only the parent
  `TimeoutError` needs is mirrored (ADR 34).
