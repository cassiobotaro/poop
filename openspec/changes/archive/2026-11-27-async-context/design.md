# Design

## Context

See proposal.md, *Why*. Two ADRs carry this change's decisions (tasks 1.1
and 1.2): the asynchronous forms defer their run to the await while the
synchronous ones refuse a coroutine, and `TimeoutError` is mirrored under an
`OSError` kept only as its parent. This document keeps what is specific to
the change. It builds on `async-methods`: `Coroutine`, `Async`, the
`await_()` rewrite and `inspect.isawaitable` as the test for "a coroutine".

What the code does today, read for this design:

- `With.do` (`poop/types/with_.py`) resolves `__enter__`/`__exit__` on the
  type through `_protocol` and `_slot`, checks the body with
  `_require_block` before entering, and is single-use through `_done`.
- `Try._execute` (`poop/types/try_.py`) is the one place `run()` and
  `finally_()` both reach. `finally_` is terminal: it stores the cleanup and
  executes.
- `_HIERARCHY` in `poop/types/exceptions.py` builds each mirror from its
  native class and its POOP parent's name, and `MirrorName` lists the keys;
  `test_mirror_names_match_the_hierarchy` keeps them in step.
- On 3.15.2, `async with 5` fails with `'int' object does not support the
  asynchronous context manager protocol (missed __aexit__ method)`,
  `asyncio.timeout` raises a `TimeoutError` with an empty message whose MRO
  runs through `OSError`, and a second `async with` on the same `Timeout`
  raises `Timeout has already been entered`. All three were run.

## Goals / Non-Goals

**Goals:**
- A failure raised at an await is caught by a guard written around it.
- The synchronous forms can no longer lose a coroutine's failure or body in
  silence.

**Non-Goals:**
- A shared base class for `With` and `AsyncWith`. They share the protocol
  lookup, not a lifecycle.

## Decisions

1. **`_protocol` takes the pair of slot names it resolves.** `With` asks
   for `__enter__`/`__exit__` and words "the context manager protocol";
   `AsyncWith` asks for `__aenter__`/`__aexit__` and words "the
   asynchronous context manager protocol". The wording stays POOP's, which
   names the half that is missing instead of the dunder (ADR 26, ADR 44).

2. **`AsyncWith.do` checks the body block, marks itself done, and answers a
   `Coroutine` over a private `async def`** that enters, calls the body,
   refuses a non-awaitable answer, awaits it, and exits, with the exit
   receiving the values `With` hands its own (mirror class, `Error`, `none`).
   The body is called after entering, so a body that answers no coroutine
   is refused from inside the manager, and the manager is exited by the
   same `try`/`finally` that exits it on any failure.

3. **`Try.__await__` drives a private `async def _execute_async`** that
   mirrors `_execute`: the same single-use flag, the same handler match, the
   same `else_` placement. Each of the block's, a handler's and `else_`'s
   answers goes through one helper that awaits it when it is awaitable. The
   block's answer alone is refused when it is not, since a `Try` awaited
   over a value is the mistake `run()` exists for. Duplicating the control
   flow of `_execute` is accepted over threading `async` through it: a
   synchronous `_execute` that returned a coroutine would change what
   `run()` answers.

4. **`_execute` refuses an awaitable answer from the protected block**, and
   closes it first. `finally_` words the refusal differently from `run`
   because `.await_()` is not a remedy there: a `Try` with a cleanup is
   already executing. `With.do` refuses an awaitable body answer the same
   way, after its exit has run.

5. **`Timeout` wraps `asyncio.timeout(delay)`**, delegating `__aenter__` and
   `__aexit__` and answering itself from `__aenter__`, so the body receives
   the POOP value. `expired()` answers `Boolean` from the wrapped object.
   The wrapped manager's own single-entry check raises the second-entry
   failure, matched by the `RuntimeError` mirror.

6. **`OSError` joins `_HIERARCHY` under `Exception`, and `TimeoutError`
   under `OSError`**, both added to `MirrorName` and bound in `mirrors.py`.
   The comment above `_HIERARCHY` that says POOP mirrors no `OSError`
   subtree is reworded to say why the one branch exists.

## Risks / Trade-offs

- **[Duplicated `Try` control flow]** `_execute` and `_execute_async` can
  drift. → Task 3.2 runs the existing `try-type` scenarios through both
  paths from one parametrised test.
- **[Timing tests]** The timeout scenarios depend on the clock. → Tests use
  a deadline of 0.01 s against a sleep of 1 s, two orders of magnitude
  apart.
- **[A body refused after side effects]** A body that answers no coroutine
  runs before it is refused, inside the manager. → Accepted: the answer
  cannot be known before the body runs, and the manager still exits.
