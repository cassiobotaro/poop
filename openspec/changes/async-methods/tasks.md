# Tasks

## 1. Decisions

- [x] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated the day it is written, status Accepted. It records that `async def` is a method in a class body and `await` is the message `x.await_()`, rewritten to `await x`, on ADR 7's test (a prefix keyword reads as procedure) and because `x.await` does not parse. It amends ADR 9: async is no longer a definitive ban; `await` is an ordinary ban with a substitute. Run the `unslop` skill on it. Verify: the filename carries the next number, ADR 9 changes only by an `Amended by` line in its Status section, and the record cites no change name.
- [x] 1.2 Write the ADR that an async method answers a `Coroutine`, a POOP value that delegates `__await__`, wrapped once at class build (design, decision 1), and why the raw coroutine is not accepted as a leak: `cr_frame` would be the first frame object a program could reach. Run `unslop`. Verify as in 1.1.
- [x] 1.3 Write the ADR that `Async` runs coroutines: named after the keyword as `Try` and `With` are, not `Asyncio`, with `run`, `sleep` and `gather` only, and what is left out (tasks, cancellation, `TaskGroup`). Run `unslop`. Verify as in 1.1.

## 2. Validators

- [x] 2.1 In `poop/validators/no_async.py`, drop the `AsyncFunctionDef` row and reword the `Await` row to `await is forbidden — use x.await_() instead`; update the module comment. Update its tests to the `no-async-validator` spec and the `ast.Await` and `ast.AsyncFunctionDef` rows of `MIGRATION.md`. Verify: `uv run pytest tests/ -k no_async` exits 0 with its summary line read.
- [x] 2.2 Add `poop/validators/no_misplaced_await.py` (design, decision 4), register it after `no_async` in `poop/validators/__init__.py`, and test every scenario of the `no-misplaced-await-validator` spec. Add its rows to `MIGRATION.md` and raise the count in `README.md` to 74. Verify: `uv run pytest tests/ -k "misplaced_await or doc_counts"` exits 0.
- [x] 2.3 In `poop/validators/no_dunder_def.py`, refuse an async dunder other than `__call__`, `__aenter__` and `__aexit__`, with the sentences of the `no-dunder-def-validator` delta; add its `MIGRATION.md` row. Verify: `uv run pytest tests/ -k dunder_def` exits 0.
- [x] 2.4 Reword the `async for` row of `no_loops.py` and the `async with` row of `no_with.py` to the sentences of their specs, and their `MIGRATION.md` rows. Verify: `git grep -n "see the async def ban"` is empty and `uv run pytest tests/ -k "no_loops or no_with"` exits 0.
- [x] 2.5 Alias `visit_AsyncFunctionDef` to `visit_FunctionDef` in `no_dunder_name.py`, with a test that a dunder name in an async method is labelled a local, as it is in a `def` (without the alias it read as a class attribute). Verify: `uv run pytest tests/ -k dunder_name` exits 0.

## 3. Async methods through the transformers

- [x] 3.1 Alias `visit_AsyncFunctionDef` in `ReturnTransformer`, `VarargsTransformer` and `StrTransformer`, and add tests for the *Falling off the end*, *Variadic arguments* and *A docstring stays a docstring* scenarios of `async-methods`, driving the method by awaiting it with a bare `asyncio.run` in the test until `Async` exists. Verify: `uv run pytest tests/ -k "return_ or varargs or string"` exits 0.

## 4. Coroutine

- [x] 4.1 Add `poop/types/coroutine.py` with `Coroutine` (design, decision 2) and its tests for the `coroutine-type` spec, building it directly from a raw coroutine. Verify: `uv run pytest tests/test_types/test_coroutine.py` exits 0.
- [x] 4.2 In `PoopMeta.__new__`, replace every coroutine function in the class namespace with its wrapping function (design, decision 1). Test that a send, `super().m()`, `get_attr("m")` and an `async def __call__` each answer a `Coroutine`, and that an async method's class still prints its own methods with `dir()`. Verify: `uv run pytest tests/test_types/test_coroutine.py tests/test_message_descriptors.py` exits 0.
- [ ] 4.3 Run a recursive async method in `tests/test_recursion.py`, at the depth its synchronous tests use, and record in the ADR of 1.2 whether ADR 61's sizing holds for an awaited send. Verify: the test passes, or the ADR names the factor and a test pins it.

## 5. await_

- [ ] 5.1 Add `poop/transformers/await_.py` and put `AwaitTransformer` first in `_TRANSFORMER_CLASSES` (design, decision 3). Test every scenario of the `await-transformer` spec. Verify: `uv run pytest tests/ -k await` exits 0.

## 6. Async

- [ ] 6.1 Add `poop/types/async_.py` with `Async` (design, decision 5) and `poop/transformers/async_.py` with its `NAMESPACE`, and add it to `_BINDING_SOURCES`. Test every scenario of the `async-type` spec and the last one of `async-methods`, replacing the bare `asyncio.run` of task 3.1 with `Async.run`. Verify: `uv run pytest tests/test_types/test_async.py` exits 0 and `uv run poop -` on `Async = 1` fails validation.
- [ ] 6.2 Update `AGENTS.md` ("no async" and "exactly two user-facing names", now three: `Try`, `With`, `Async`) and `CONTRIBUTING.md` where it says the same. Add an *Async methods* section to `README.md` and the `asyncio.run` → `Async.run` row to `MIGRATION.md`'s substitute table; run every snippet added. Verify: each snippet runs with `uv run poop` and prints what the doc says.
- [ ] 6.3 Add `examples/idiomatic/concurrent_fetch.py`, a class whose async methods are gathered, with its Smalltalk equivalent in the docstring (`(Delay forSeconds: 1) wait` for `Async.sleep`, `fork` and a `Semaphore` for `gather`). List it in `examples/README.md` and raise the count to 45. Verify: `uv run poop examples/idiomatic/concurrent_fetch.py` runs and `uv run pytest tests/test_doc_counts.py` exits 0.

## 7. Integration

- [ ] 7.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check`, `uv run ty check poop/ tests/`, and every example; `tests/test_no_python_wording.py` and `tests/test_examples_docstring.py` are part of the suite and cover the new sentences and the new example. Verify: each command exits 0.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*) before applying `async-context`, whose specs build on these.
