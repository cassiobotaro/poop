# Design

## Context

- `poop_message` (`poop/types/_message.py`) is where POOP rewords a CPython
  sentence. The uncaught report (`describe`), `Error.message()` and a
  mirror's own message all read it. It already rewords the operator shapes
  and `holds_no_state` with one regex each.
- `x.await_()` is syntax: `AwaitTransformer` rewrites it to `await x`, so
  the failure is CPython's `TypeError: '<class>' object can't be awaited`,
  raised by the interpreter and never by POOP's own code.
- `refuse_awaitable` (`poop/types/coroutine.py`) gives `Try.run`,
  `Try.finally_` and `With.do` one sentence for anything `isawaitable`
  accepts. The only POOP awaitables are a `Coroutine` and a `Try`.

## Goals / Non-Goals

**Goals:**
- Every failure from awaiting a value that cannot be awaited reads in POOP's
  words, however it is read.
- A refusal names what the block answered, a coroutine or a `Try`.

**Non-Goals:**
- Changing the class of any failure. Both stay `TypeError`, as CPython raises.

## Decisions

**The await_ sentence is reworded in `poop_message`, not at the await.**
A new `_UNAWAITABLE` pattern, `^'(.+?)' object can't be awaited$`, maps to
`{class} cannot be awaited — send #await_ to a coroutine, the value an async
method answers`. The class is the one CPython printed, which is already
POOP's cloaked name. The alternative is to have `AwaitTransformer` rewrite
`x.await_()` to `await _poop_awaitable(x)`, a helper that checks first. That
adds a mangled binding and a Python call to every await, and it would only
cover awaits a program writes, while `poop_message` covers them all at no
cost on the success path. The remedy is spelled `#await_` because
`test_no_python_wording` refuses `await_()` as a call in a message.

**`refuse_awaitable` tells a `Try` from a `Coroutine`.** It takes the owner
(`the Try block`, `the With body`) as well as today's coroutine sentence.
When the value is awaitable and not a `Coroutine`, it raises `{owner}
answered a Try that has not run — send #run to it`. Branching on "not a
`Coroutine`" rather than on `Try` keeps `coroutine.py` from importing
`try_.py`, which imports it. The only other awaitable a program can hold is
a `Try`. If that changes, a test that refuses a new awaitable will show the
sentence is wrong, because the test quotes it.

**The `Try` documentation goes where the awaited `Try` is already
described.** `README.md` gets one sentence after the `Feed` example.
`MIGRATION.md`'s row for `.await_()` on `Try` (the *Try* table) names
`Async.run` and `Async.gather` as other places a `Try` can be awaited.

## Risks / Trade-offs

- [CPython rewords `can't be awaited`] → The pattern stops matching and the
  raw sentence comes back. The `await-transformer` scenarios quote the POOP
  sentence, so a test fails instead of drifting silently.
- [The `_slot` docstring in `async_with.py` quotes the old sentence] → It
  is updated in the same commit as the rewording.
