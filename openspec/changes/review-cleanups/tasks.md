# Tasks

## 1. Cleanups

- [x] 1.1 Remove `executor._describe` and call `describe` in `execute`. Add to `describe`'s docstring (`poop/types/exceptions.py`) the reason `_describe`'s docstring gave and `describe`'s does not: `str(exc)` alone drops the class, so a missing key would render as the bare `'zzz'`. Point the comments that name `_describe` at `describe`, in `poop/executor.py`, `poop/types/_message.py`, `poop/types/error.py`, `tests/test_no_python_wording.py` and `tests/test_types/test_iterator_base.py`. Verify: `git grep -n "_describe" -- poop tests` is empty, and `uv run pytest tests/test_executor.py tests/test_no_python_wording.py tests/test_types/test_iterator_base.py tests/test_types/test_error.py` exits 0 with its summary line read.
- [ ] 1.2 In `poop/transformers/base.py`, raise the native `TypeError` from `BaseTransformer.__init_subclass__` and remove the `poop.types.mirrors` import. In `tests/test_transformers/test_base.py`, assert that the class raised is exactly `TypeError`. Verify: `git grep -n "mirrors" -- poop/transformers/base.py` is empty, and `uv run pytest tests/test_transformers` exits 0 with its summary line read.

## 2. Integration

- [ ] 2.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check` and `uv run ty check poop/ tests/`. Run `printf '(1).at(0)\n' | uv run poop -`. Verify: every gate command exits 0, and the program exits 4 with its `poop: ` report unchanged from before the change.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*).
