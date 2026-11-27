# Proposal

## Why

A review of the async implementation turned up three gaps. The worst one breaks ADR 76's guarantee
that every async method of a POOP class answers a `Coroutine`: an
`@property async def` answers CPython's raw coroutine, so `cr_frame`, `send`
and `throw` are within a program's reach and an unknown message fails in
CPython's words. The other two are smaller. A refusal can leave behind a
coroutine that was never awaited, and an asynchronous manager whose slot
cannot be awaited is reported in generic `await` words.

## What Changes

- An `@property async def` getter answers a `Coroutine`, the value every
  other async method answers. The getter can still be awaited, as it can in
  CPython.
- When `Async.gather` refuses an argument, it first closes the `Coroutine`s
  it was handed before that argument. When `Async.run` is sent inside a
  running event loop, it closes the `Coroutine` it was handed before failing
  with CPython's sentence. Neither refusal leaves a "never awaited" warning
  behind, the same behaviour `refuse_awaitable` already gives `Try.run` and
  `With.do`.
- When `AsyncWith` awaits an `__aenter__` or `__aexit__` that answers a value
  that cannot be awaited, it fails with a POOP sentence that names the
  manager, the slot and what it answered, and hints at `async def`. Today it
  reports `'Res' object can't be awaited`. CPython's own `async with`
  sentence names `__aenter__` and `__await__`, and
  `tests/test_no_python_wording.py` refuses a dunder in any failure a program
  can reach, so POOP rewords it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `async-methods`: an async method reached as a property answers a
  coroutine.
- `async-type`: a refusal from `run` or `gather` closes the coroutines it
  was handed.
- `async-with-type`: a manager slot that cannot be awaited is refused in
  POOP's words.

## Impact

- `poop/types/meta.py` (`_answering_a_coroutine`)
- `poop/types/async_.py` (`run`, `gather`)
- `poop/types/async_with.py` (`_entered`)
- Tests in `tests/test_async_methods.py`, `tests/test_types/test_async.py`,
  `tests/test_types/test_async_with.py` and
  `tests/test_no_python_wording.py`.
- `MIGRATION.md`'s async section, if it describes property getters. No new
  ADR: each fix applies a decision that already exists (ADR 76, ADR 80, and
  the rule that a reachable failure names no Python construct).

## Out of scope

- **Every `Try` can be awaited.** `Try` defines `__await__`, so
  `Async.run(Try(...))` works. A synchronous block that answers an
  unexecuted `Try` is therefore refused as "answered a coroutine". ADR 80
  intends the awaited `Try`, and the wording case needs a `Try` that answers
  another `Try` unrun, which no program in `examples/` writes. Changing it
  would mean a second refusal sentence for one corner case.
- **Async setters and deleters.** `no_decorator` accepts only a bare
  `@property`, so a program cannot write `@x.setter`, and no other accessor
  can be async.
- **CPython's own leak in `asyncio.run`.** Only the `Coroutine` POOP was
  handed is closed. A coroutine CPython creates internally is CPython's
  responsibility.
