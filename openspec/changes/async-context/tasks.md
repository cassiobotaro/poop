# Tasks

## 1. Decisions

- [x] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated the day it is written, status Accepted. It records that `AsyncWith` and an awaited `Try` defer their run to the await, that a handler or `else_` of an awaited `Try` may answer a value or a coroutine while its block must answer a coroutine, and that `Try.run`, `Try.finally_` and `With.do` refuse a coroutine rather than lose its failure or body. It extends ADRs 26 and 54. Run the `unslop` skill on it. Verify: the filename carries the next number, ADRs 26 and 54 are untouched, and the record cites no change name.
- [x] 1.2 Write the ADR that `TimeoutError` is mirrored under `OSError`, which is mirrored only as its parent, following CPython's tree over a flatter one; it extends ADR 34. Run `unslop`. Verify as in 1.1.

## 2. Mirrors

- [x] 2.1 Add `OSError` and `TimeoutError` to `_HIERARCHY`, `MirrorName` and `mirrors.py` (design, decision 6), and test the `exception-mirrors` delta's *Raised and reported* and *OSError's parent* scenarios. Verify: `uv run pytest tests/test_mirrored_raises.py tests/test_types -k "mirror or exception"` exits 0.

## 3. The synchronous forms refuse a coroutine; the awaited Try

- [x] 3.1 In `Try._execute` and `With.do`, refuse and close an awaitable answer (design, decision 4), and test the *run and finally_ refuse a block that answers a coroutine* requirement of `try-type` and the `with-type` delta. Add the rows to `MIGRATION.md`. Verify: `uv run pytest tests/test_types -k "try or with"` exits 0.
- [x] 3.2 Add `Try.__await__` (design, decision 3) and test every scenario of the *awaited Try* requirements except *A timeout is caught*, which task 5.1 adds. Parametrise the existing `else_` and handler tests to run through `run()` and through an awaited `Try`. Document the awaited `Try` in `README.md` and `MIGRATION.md` and run each snippet. Verify: `uv run pytest tests/test_types -k try` exits 0.

## 4. AsyncWith

- [ ] 4.1 Generalise `_protocol` to take its slot pair and wording (design, decision 1). Verify: the existing `With` tests pass unchanged with `uv run pytest tests/test_types -k with`.
- [ ] 4.2 Add `poop/types/async_with.py` with `AsyncWith` (design, decision 2) and `poop/transformers/async_with.py` with its `NAMESPACE`, added to `_BINDING_SOURCES`. Test every scenario of `async-with-type`, using a user class with `async def __aenter__`/`__aexit__` as the manager. Verify: `uv run pytest tests/test_types/test_async_with.py` exits 0.
- [ ] 4.3 Reword the `async with` row of `no_with.py` to the `no-with-validator` delta and its `MIGRATION.md` row; update `AGENTS.md` and `CONTRIBUTING.md` to four user-facing names. Verify: `uv run pytest tests/ -k no_with` exits 0.

## 5. Timeout

- [ ] 5.1 Add `poop/types/timeout.py` with `Timeout` (design, decision 5) and `Async.timeout`, and reword `Async()`'s refusal to the `async-type` delta. Test every scenario of `timeout-type` and the `async-type` delta, the *A timeout is caught* scenario of `try-type`, and the *Caught by its parent* scenario of `exception-mirrors`. Document `Async.timeout` in `README.md` and run the snippet. Verify: `uv run pytest tests/test_types -k "timeout or async"` exits 0.
- [ ] 5.2 Add `examples/idiomatic/deadline.py`, a fetch guarded by `Async.timeout` inside an awaited `Try` and an `AsyncWith` over a user manager, with its Smalltalk equivalent in the docstring (Pharo's `[ … ] valueWithin: 1 second onTimeout: [ … ]` and `ensure:`). List it in `examples/README.md` and raise the count to 46. Verify: `uv run poop examples/idiomatic/deadline.py` runs and `uv run pytest tests/test_doc_counts.py tests/test_examples_docstring.py` exits 0.

## 6. Integration

- [ ] 6.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check`, `uv run ty check poop/ tests/`, and every example. Verify: each command exits 0.

## Workflow follow-up

- Apply only after `async-methods` is archived: the `async-type` and `no-with-validator` deltas modify specs that change creates.
- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*).
