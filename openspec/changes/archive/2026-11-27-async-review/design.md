# Design

## Context

Each of the three fixes lands in a different file. All three apply
decisions that already exist (see proposal.md, Impact), so this change adds
no ADR.

- `_answering_a_coroutine` (`poop/types/meta.py`) runs on every entry of a
  program's class body when the class is built. It already looks through a
  `staticmethod` or `classmethod` to the function it wraps. A `property` is
  a third kind of wrapper whose function, `fget`, it does not look into.
- `refuse_awaitable` (`poop/types/coroutine.py`) closes a `Coroutine`'s raw
  coroutine before it refuses, so CPython emits no "never awaited" warning.
  `Async.run` and `Async.gather` refuse without closing.
- `_entered` (`poop/types/async_with.py`) awaits whatever `__aenter__` and
  `__aexit__` answer, and an `await` on a value that cannot be awaited fails
  with CPython's generic sentence.

## Goals / Non-Goals

**Goals:**
- Every value a program reads from an async getter is a POOP `Coroutine`.
- A refusal from `Async.run` or `Async.gather` leaves no live coroutine
  behind.

**Non-Goals:**
- Closing coroutines CPython creates internally. Closing the value the
  program handed in is enough to suppress its warning.
- Rewording the generic `can't be awaited` sentence anywhere outside
  `AsyncWith`. `x.await_()` on a non-awaitable keeps CPython's sentence for
  a bare `await`, which is what CPython says there too.

## Decisions

**A property's getter is wrapped, not refused.** `_answering_a_coroutine`
treats a `property` the way it treats a `staticmethod`. When the `fget` is a
coroutine function, it rebuilds the property with `entry.getter(wrapped)`,
which keeps `fset`, `fdel` and the docstring. The alternative is a validator
that refuses `async def` under `@property`. CPython accepts that form, and
ADR 76 already says every way of reaching an async method answers a
`Coroutine`, so refusing it would be a new decision, and this change has no
reason to make one. Only `fget` can be async: `no_decorator` accepts only a
bare `@property`, so a program has no way to attach a setter.

**`Async.run` checks for a running loop itself.** When one is running, it
closes the coroutine and still calls `asyncio.run`, which refuses in its own
words, `asyncio.run() cannot be called from a running event loop`, before it
touches its argument. The alternative of catching `RuntimeError` from
`asyncio.run` cannot tell asyncio's refusal from one the coroutine's own body
raises. Raising a copy of the sentence from POOP was tried during
implementation: `tests/test_no_python_wording.py` refuses `asyncio.run()` in
a POOP-authored message, and a copy could drift from CPython.

**`Async.gather` validates first and closes on refusal.** The arguments are
already created when `gather` receives them. On a refusal, it closes every
`Coroutine` among them, using the same close that `refuse_awaitable`
performs. An awaitable that is not a `Coroutine`, such as an unexecuted
`Try`, holds no running coroutine, so there is nothing to close.

**`AsyncWith` checks each slot's answer before awaiting it.** A small helper
in `async_with.py` raises the `TypeError` mirror with
`{Manager}'s asynchronous {enter|exit} answered {describe_operand(answer)},
which cannot be awaited — write it as async def`. `Manager` is the manager's
class `__name__`, so POOP's cloaked names come out as a program spells them.
CPython's sentence names `__aenter__` and `__await__`. The second one is not
something a program writes, and `tests/test_no_python_wording.py` refuses a
dunder in a reachable failure, so `enter` and `exit` follow the
`asynchronous context manager protocol` wording `protocol_of` already uses.
The new sentence is added to that test's samples.

## Risks / Trade-offs

- [A future CPython touches its argument before refusing] → The "Run
  inside run" test would then fail on the recorded warning, not pass
  silently.
- [A subclass that overrides an async property with a sync one, or the
  reverse] → Each class body is wrapped on its own, so each override
  answers what its own getter is. This is no different from methods today.
