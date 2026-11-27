# Proposal

## Why

ADR 9 lists `async def` and `await` as definitive bans because dropping the
stdlib mirrors left nothing that could drive a coroutine. That premise is the
only thing holding the ban: give a program a way to run a coroutine and an
async method becomes a message like any other. This change gives it one, and
spells `await` as a message, `x.await_()`, since a prefix keyword reads as
procedure by the test of ADR 7, the same test that turned `not x` into
`x.not_()`.

## What Changes

- **`async def` is allowed as a direct statement of a class body.** It is a
  method, as a `def` there is (ADR 68). Everywhere else it stays refused by
  `no_free_functions`, with the sentence it answers today.
- **`await x` stays refused, now with a substitute**: `no_async` answers
  `await is forbidden — use x.await_() instead`. It is no longer a definitive
  ban, so it follows the ordinary rule of ADR 9.
- **New `AwaitTransformer`** rewrites `x.await_()` to `await x`. `await` is a
  keyword, so `x.await()` does not parse; the trailing underscore is the
  spelling POOP already uses for `and_`, `except_` and `raise_`.
- **New validator `no_misplaced_await`** refuses every use of the `await_`
  selector the rewrite cannot honour: outside an async method (module level,
  a synchronous method), inside a block, with arguments, read without being
  sent, and `def await_` in a class body, which would be shadowed by the
  rewrite.
- **`no_dunder_def` refuses an `async def` dunder** other than `__call__`,
  `__aenter__` and `__aexit__`: Python calls the rest without awaiting them.
- **An async method answers a `Coroutine`**, a POOP value cloaked as
  `coroutine` that delegates `__await__`. It answers `Object`'s messages,
  prints as `<coroutine>`, and keeps the raw coroutine's attributes
  (`cr_frame`, `send`, `throw`) out of reach.
- **New injected name `Async`**, a class named after the keyword as `Try` and
  `With` are, with three class-side messages: `Async.run(coroutine)`,
  `Async.sleep(delay, result=none)` and `Async.gather(*coroutines)`. Each
  answers POOP values; `gather` answers a `List`.
- **`ReturnTransformer`, `VarargsTransformer`, `StrTransformer` and
  `no_dunder_name` learn `AsyncFunctionDef`**, which they skip today because
  no async def could reach them.
- **`no_loops` and `no_with` reword their async rows**, which point at "the
  async def ban" this change removes.
- **Three ADRs**: await is a message; an async method answers a `Coroutine`;
  `Async` is the language's runner, not a mirror of `asyncio`. The first
  amends ADR 9.
- **Docs**: `AGENTS.md` ("no async", "exactly two user-facing names"),
  `README.md` (validator count, a section on async methods), `MIGRATION.md`
  (the ban table and the substitute rows), and a new example.

## Capabilities

### New Capabilities
- `async-methods`: an `async def` in a class body is a method that answers a
  coroutine, with POOP's return and variadic rules.
- `coroutine-type`: what a coroutine answers before and after it is awaited.
- `async-type`: `Async.run`, `Async.sleep`, `Async.gather` and the refusals
  of each.
- `await-transformer`: `x.await_()` awaits `x` inside an async method.
- `no-async-validator`: `await` refused with its substitute.
- `no-misplaced-await-validator`: the misuses of `await_` and their sentences.
- `no-loops-validator`: the `async for` row's wording.
- `no-with-validator`: the `async with` row's wording.

### Modified Capabilities
- `no-dunder-def-validator`: an async dunder outside `__call__`, `__aenter__`
  and `__aexit__` is refused.

## Impact

- New: `poop/types/coroutine.py`, `poop/types/async_.py`,
  `poop/transformers/await_.py`, `poop/transformers/async_.py`,
  `poop/validators/no_misplaced_await.py`, three ADRs, one example.
- Edited: `poop/types/meta.py` (wrapping at class build),
  `poop/transformers/_registry.py`, `return_.py`, `varargs.py`, `string.py`,
  `poop/validators/__init__.py`, `no_async.py`, `no_dunder_def.py`,
  `no_dunder_name.py`, `no_loops.py`, `no_with.py`, and their tests.
- `DEFAULT_NAMESPACE` grows from two user-facing names to three. The
  protected set of `no_namespace_shadow` is derived from it and follows on its
  own.
- No program that runs today changes behaviour: every construct this change
  admits is refused now.

## Out of scope

- **`async with`, an awaited `Try`, `Async.timeout`, `TimeoutError`.** They
  are the `async-context` change, which builds on this one.
- **`async for` and asynchronous iterators.** No POOP value is an
  asynchronous iterator, and an async generator is refused by `no_yield`.
- **`create_task`, `TaskGroup`, cancellation.** A task is a handle a program
  would have to hold and cancel, and `TaskGroup` raises an `ExceptionGroup`,
  which brings back the `except*` ban of ADR 9. Neither is needed to run and
  combine coroutines.
- **`gather(return_exceptions=…)` and `run(debug=…, loop_factory=…)`.** The
  first would put exceptions in a `List` as values, which needs its own
  decision about what an element is; the second hands a program a Python
  event loop factory. `Async` is not a builtin substitute, so ADR 39's
  full-signature rule does not bind it.
- **Turning the "never awaited" warning into an error.** CPython's
  `RuntimeWarning` stays, as POOP follows CPython where nothing argues
  otherwise.
- **Top-level `await_()` in the REPL.** `Async.run` works there as it does in
  a file.
