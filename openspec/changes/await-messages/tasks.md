# Tasks

Each numbered group is one commit, a `fix(types): ...` with its tests and
docs. "The gate" in a task below means all of these pass:

- `uv run pytest` exits 0 with its summary line read (95% coverage floor).
- `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/`
  exit 0.

## 1. await_ on a value that cannot be awaited

- [x] 1.1 Add tests for both `await-transformer` scenarios next to the existing `await_` tests (find them with `grep -rln "await_" tests/test_transformers`). Add the "Awaiting an int" program to `_FAILING` in `tests/test_no_python_wording.py`. Verify: the scenario tests fail on `main` with `'int' object can't be awaited`.
- [x] 1.2 Add `_UNAWAITABLE` to `poop/types/_message.py` and reword it in `poop_message`, and update `poop_message`'s docstring, which counts the shapes it rewords. Update the `_slot` docstring in `poop/types/async_with.py`, which quotes the old sentence. Verify: the 1.1 tests pass, and so does the gate.
- [x] 1.3 In `MIGRATION.md`, add the sentence to the `x.await_()` notes under *Async methods* if they list failures; otherwise leave the doc unchanged and say so in the commit body. Run any snippet added. Verify: the commit body or `git diff MIGRATION.md` shows which.

## 2. A block that answers a Try that has not run

- [x] 2.1 Add tests for the `try-type` scenarios (`run`, `finally_`) in `tests/test_types/test_try_.py` and the `with-type` scenario in `tests/test_types/test_with_.py`, the last one asserting `exit` is printed. Verify: the three fail on `main` with `answered a coroutine`.
- [x] 2.2 Give `refuse_awaitable` the owner, and raise the `Try`-not-run sentence for an awaitable that is not a `Coroutine`. Pass `the Try block` from both `_execute` callers in `poop/types/try_.py` and `the With body` from `poop/types/with_.py`. Verify: the 2.1 tests pass, the existing coroutine-refusal tests still pass, and so does the gate.

## 3. Async.run and Async.gather accept an awaited Try

- [ ] 3.1 Add tests for both `async-type` scenarios in `tests/test_types/test_async.py`. Verify: they pass on `main`, since the behavior exists, and they fail if `Try.__await__` is removed locally. Restore it.
- [ ] 3.2 Add one sentence to `README.md` after the `Feed` example saying `Async.run` and `Async.gather` take an awaited `Try` too, with a runnable snippet, and name both in `MIGRATION.md`'s `.await_()` row of the *Try* table. Run the snippet with `uv run poop`. Verify: it prints what the README says, and `uv run pytest tests/test_doc_counts.py` passes.

## 4. Close

- [ ] 4.1 Run `openspec validate await-messages --strict` and the two async examples (`examples/idiomatic/concurrent_fetch.py`, `examples/idiomatic/deadline.py`). Verify: validate exits 0 and the examples print what their docstrings say.

## Workflow follow-up

- Archive the change with `/openspec-archive-change` once the gate passes on `main`.
