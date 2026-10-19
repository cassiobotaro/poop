# Tasks

## 1. try/else

- [x] 1.1 Add `Try.else_` (new `_else_block` slot, `_require_block` with role `the else clause`, refusal of a second `else_`, ignored once executed) and an `else:` branch in `_execute` that replaces `result` with the block's value; add the `try-type` delta's eight scenarios to `tests/test_types/test_try_.py`, the non-block and second-`else_` refusals to the wording sweep, and an `else_` row and paragraph to *Try* in `INFECTIONS.md`; verify `uv run pytest tests/test_types/test_try_.py tests/test_no_python_wording.py -q` passes and every new doc snippet runs with `uv run poop`.

## 2. Exception chaining

- [x] 2.1 Add the instance-side `raise_from(cause)` beside the instance `raise_` in `poop/types/exceptions.py`, resolving an `Error`, a built instance or `None` before raising and refusing anything else, a missing cause or more than one with `#raise_from takes an exception or None, got …`; add the `exception-mirrors` delta's `raise_from` scenarios to `tests/test_types/test_exceptions.py` and the four refusals as programs in the wording sweep's `_FAILING` list; document it under *PoopExcMeta* in `INFECTIONS.md` with the `raise X from Y` mapping and the class-side omission; verify `uv run pytest tests/test_types/test_exceptions.py tests/test_no_python_wording.py -q` passes.
- [x] 2.2 Add `Error.cause()` and `Error.context()` answering an `Error` or `none`, with `context()` answering `none` when the context is suppressed; add the `error-type` delta's five chain scenarios to `tests/test_types/test_error.py`, including `[1].at(5)` having no context; extend *Error* in `INFECTIONS.md` with both messages and the `from None` reason for the divergence from the raw dunder; verify `uv run pytest tests/test_types/test_error.py -q` passes.
- [x] 2.3 Make the instance-side `raise_` and `Error.raise_` take `*extra` and refuse it with `#raise_ takes no argument once the exception is built, got N argument(s)` / `#raise_ takes no argument on a caught error, got N argument(s)`; add both cases to `tests/test_types/test_exceptions.py` / `tests/test_types/test_error.py`, the built-exception one as a `_FAILING` program (the `Error` sample already sends `raise_` a wrong argument once it takes one); verify `uv run pytest tests/test_types/test_exceptions.py tests/test_types/test_error.py tests/test_no_python_wording.py -q` passes and neither program answers `positional argument`.

## 3. The chain in the report

- [x] 3.1 Add the chain walk beside `describe` (cause, else an unsuppressed context, stopping at `None` or an exception already seen), let `ExecutionError` carry its lines from both `execute` paths, and print them after the quoted source line in `format_error` / `render_error`, indented two spaces (a run-time failure has no caret); add the `cli` delta's four scenarios to `tests/test_cli.py`, a cycle case and a plain/styled rendering case to `tests/test_errors.py`, and one REPL case to `tests/test_repl.py`; update any existing test whose stderr gains a line; document the report format in `INFECTIONS.md`; verify `uv run pytest tests/test_cli.py tests/test_errors.py tests/test_executor.py tests/test_repl.py -q` passes.

## 4. except* as a definitive ban

- [x] 4.1 Change `no_try`'s `ast.TryStar` sentence to `try/except* is forbidden — nothing in POOP raises an exception group`, add an `except*` statement to the `:explain try` snippet in `poop/repl.py`, add the `no-try-validator` delta's three scenarios to `tests/test_validators/test_no_try.py`, and move `except*` into the definitive-ban list in *Principles* and under *No `try`* in `INFECTIONS.md`; verify `uv run pytest tests/test_validators/test_no_try.py tests/test_repl.py tests/test_doc_counts.py -q` passes and `grep -rn "except\*" poop/validators INFECTIONS.md` shows no substitute.

## 5. Integration

- [x] 5.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the summary line explicitly, run every example (`for f in examples/*/*.py; do uv run poop "$f" </dev/null; done`), and run `openspec validate complete-exception-protocol --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Archive the change with `/opsx:archive` once every task is done.
