# Proposal

## Why

The async review (`async-review`, archived 2026-11-27) set two refusals
aside. The first is `x.await_()` on a value that cannot be awaited: it
fails with CPython's `'int' object can't be awaited`, which gives no hint.
The usual mistake behind it is awaiting what a synchronous send answered,
as in `Try(...).run().await_()`. The second comes from `Try` defining
`__await__`. A synchronous `Try.run` or `With.do` whose block answers a
`Try` it never ran is refused as having "answered a coroutine", which is
not what happened. The same `__await__` is also why `Async.run(Try(...))`
and `Async.gather(Try(...))` work, and no doc says they do.

## What Changes

- `x.await_()` on a value that cannot be awaited fails with
  `int cannot be awaited — send #await_ to a coroutine, the value an async
  method answers`. It is still a `TypeError`, as in CPython.
- When a `Try.run`, `Try.finally_` or `With.do` block answers a `Try` that
  has not run, the refusal says so: `the Try block answered a Try that has
  not run — send #run to it`, and the same sentence with `the With body`
  for `With.do`. A block that answers a coroutine keeps today's sentence.
- `Async.run` and `Async.gather` accepting an awaited `Try` becomes
  specified behavior, and `README.md` and `MIGRATION.md` say so.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `await-transformer`: a receiver that cannot be awaited is refused in
  POOP's words.
- `try-type`: `run` and `finally_` name a `Try` that has not run, instead of
  calling it a coroutine.
- `with-type`: `do` names a `Try` that has not run, instead of calling it a
  coroutine.
- `async-type`: `run` and `gather` accept an awaited `Try`.

## Impact

- `poop/types/_message.py` (`poop_message`)
- `poop/types/coroutine.py` (`refuse_awaitable`), `poop/types/try_.py`,
  `poop/types/with_.py`
- `poop/types/async_with.py`: the `_slot` docstring quotes the sentence
  this change rewords.
- Tests: `tests/test_types/test_try_.py`, `tests/test_types/test_with_.py`,
  `tests/test_types/test_async.py`, the `await_` tests, and a sample in
  `tests/test_no_python_wording.py`.
- `README.md` and `MIGRATION.md`. No ADR: rewording a CPython sentence in
  `poop_message` is the existing practice, and ADR 80 already decided the
  awaited `Try`.

## Out of scope

- **Making `Try` not awaitable.** ADR 80 decided that a `Try` is awaited
  with `.await_()`, which needs `__await__`. The fix is in the wording, not
  the protocol.
- **An `await_` hint tailored to each receiver.** The sentence names the
  receiver's class and the remedy. Telling apart `Try(...).run().await_()`
  from other mistakes would mean inspecting the source of the expression,
  and the rewording layer sees only the exception.
