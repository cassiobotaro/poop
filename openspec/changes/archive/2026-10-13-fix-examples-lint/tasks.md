# Tasks

## 1. Lint exemptions for examples

- [x] 1.1 In `pyproject.toml`, extend the `"examples/**/*.py"` entry of `[tool.ruff.lint.per-file-ignores]` with `PLW0108` and `ARG005`, each under a comment giving its reason (block literal / `With.do` body contract); verify `uv run ruff check --statistics` reports only the one `PIE808`.
- [x] 1.2 In `examples/patterns/money.py`, change `range(0, parts)` to `range(parts)` in `allocate` (ruff's safe fix: `uv run ruff check --fix --select PIE808 examples/patterns/money.py`); verify `uv run ruff check` prints `All checks passed!`, and `uv run poop examples/patterns/money.py` prints the same output as before the edit (capture it first).
- [x] 1.3 Verify `git status --short examples/` lists only `money.py` and `uv run pytest tests/test_doc_counts.py -q` passes (no example added or removed).

## 2. Contributor note

- [x] 2.1 In `CONTRIBUTING.md` (Testing section), extend the bullet about `examples/` being excluded from `ty` and `F821` so it lists `ANN`, `PLW0108` and `ARG005` with the one reason: examples are POOP programs whose lambdas are blocks and whose shape follows the Smalltalk twin; verify the bullet reads as one sentence and `uv run ruff check` still passes.

## 3. Integration

- [x] 3.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`; verify every step exits 0.

## Workflow follow-up

- One commit (`chore(lint): ...`) carrying the three files; the hooks pass on staged files as before.
- Push and confirm the CI run on `main` is green at the lint step before archiving.
