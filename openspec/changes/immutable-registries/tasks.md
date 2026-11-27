# Tasks

## 1. Decision

- [ ] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated the day it is written, status Accepted. It records that the default validators, transformers and namespace are immutable (tuples and a `MappingProxyType`), and that an interpreter holds and hands out an immutable copy of what it was given. Verify: the filename carries the next number, and the record cites no change name.

## 2. Implementation

- [ ] 2.1 Make the registries immutable: `DEFAULT_VALIDATORS` a tuple in `poop/validators/__init__.py`, `_TRANSFORMER_CLASSES` and `DEFAULT_TRANSFORMERS` tuples in `poop/transformers/_registry.py`, and `DEFAULT_NAMESPACE` a `MappingProxyType` over `_merge_bindings(...)`, annotated `Mapping[str, object]`. Change "registered lists" to "registered tuples" in `.github/copilot-instructions.md`. In the same commit, change `Interpreter` (`poop/interpreter.py`): `validators` and `transformers` typed `Sequence[...] | None` and stored as `tuple(...)`; `namespace` typed `Mapping[str, object] | None`; the `validators` property answers `tuple[Validator, ...]`; and the comment on the copy states why the interpreter converts. Replace `test_an_interpreter_does_not_share_the_default_registry` in `tests/test_interpreter.py` with a test that `Interpreter().validators` is a tuple and that clearing the list passed as `validators=` leaves the interpreter's validators unchanged. Add a test that assigning into `DEFAULT_NAMESPACE` raises `TypeError`. Verify: `git grep -nE "DEFAULT_(VALIDATORS|TRANSFORMERS)[^=]*: list|_TRANSFORMER_CLASSES: list|DEFAULT_NAMESPACE: dict" -- poop` is empty, and `uv run pytest tests/test_interpreter.py tests/test_pipeline.py tests/test_repl.py tests/test_cloak.py tests/test_doc_counts.py` exits 0 with its summary line read.
- [ ] 2.2 Run `uv run ty check poop/ tests/` and `uv run ruff check`. Fix any annotation the new types break, in a separate commit only if one is needed. Verify: both exit 0.

## 3. Integration

- [ ] 3.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check` and `uv run ty check poop/ tests/`. Run `uv run poop examples/basics/hello_world.py` and `uv run poop --validators-only examples/basics/hello_world.py`. Verify: every command exits 0.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*).
