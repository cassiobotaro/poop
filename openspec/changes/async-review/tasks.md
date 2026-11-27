# Tasks

Each numbered group is one commit, a `fix(types): ...` with its tests and docs.
"The gate" in a task below means all of these pass:

- `uv run pytest` exits 0 with its summary line read (95% coverage floor).
- `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/`
  exit 0.

## 1. An async property answers a coroutine

- [x] 1.1 In `tests/test_async_methods.py`, add one test per scenario of the `async-methods` delta (reading runs nothing and prints `<coroutine>`, `cr_frame` is refused with the quoted sentence, awaiting answers `42`), and add the property to `test_every_way_of_reaching_an_async_method_answers_a_coroutine`. Verify: the new tests fail on `main` with `'coroutine' object has no attribute 'print'`.
- [x] 1.2 Teach `_answering_a_coroutine` (`poop/types/meta.py`) to look through a `property`: when its `fget` is a coroutine function, answer `entry.getter(wrapped)`, and update the docstring to list the property among the ways of reaching the method. Verify: the 1.1 tests pass, and so does the gate.
- [x] 1.3 If `MIGRATION.md`'s *Async methods* section or `README.md` lists the ways an async method is reached, add the property and run the snippet. Otherwise leave them unchanged and say so in the commit body. Verify: `grep -n "property" MIGRATION.md` shows the addition, or the commit body says no doc lists those ways.

## 2. A refusal from Async leaves no coroutine unawaited

- [x] 2.1 In `tests/test_types/test_async.py`, add tests for both scenarios of the `async-type` delta. Each one runs the program under `warnings.catch_warnings(record=True)` with `simplefilter("always")` and `gc.collect()`, then asserts the quoted sentence and that no recorded `RuntimeWarning` names the coroutine. Verify: both fail on `main` because the warning is recorded.
- [x] 2.2 In `poop/types/async_.py`, `run` checks for a running loop first. If one is running, it closes the handed `Coroutine` and raises `mirrors.RuntimeError("asyncio.run() cannot be called from a running event loop")`. `gather` closes every `Coroutine` it was handed before raising its refusal. Share the close with `refuse_awaitable` (`poop/types/coroutine.py`) rather than writing `_raw.close()` a second time. Verify: the 2.1 tests pass, the existing "Run inside run" test still passes, and so does the gate.

## 3. A manager slot that cannot be awaited is refused in POOP's words

- [ ] 3.1 In `tests/test_types/test_async_with.py`, add tests for both scenarios of the `async-with-type` delta, asserting the quoted sentence and, for the enter case, that the body did not run. Add the synchronous-enter program to the samples in `tests/test_no_python_wording.py`. Verify: the new tests fail on `main` with `'Res' object can't be awaited`.
- [ ] 3.2 In `poop/types/async_with.py`, check what each `enter(cm)` and `exit_(cm, …)` answers before awaiting it, in all three places `_entered` awaits a slot, and raise `mirrors.TypeError(f"{type(cm).__name__}'s asynchronous {slot} answered {describe_operand(answer)}, which cannot be awaited — write it as async def")`. Verify: the 3.1 tests pass, and so does the gate.

## 4. Close

- [ ] 4.1 Run every program in `examples/` that uses `Async` or `AsyncWith` (`examples/idiomatic/concurrent_fetch.py`, `examples/idiomatic/deadline.py`), and rerun the 25 probe programs from the review's scratchpad if they are still there. Verify: the examples print what their docstrings say, and the probes `u1`, `t2`, `t3` and `u3` give the new answers.
- [ ] 4.2 Run `openspec validate async-review --strict`. Verify: it exits 0.

## Workflow follow-up

- Archive the change with `/openspec-archive-change` once the gate passes on `main`.
