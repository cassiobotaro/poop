# Tasks

## 1. Decision

- [ ] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated the day it is written, status Accepted. It records that the exception classes and their terminal rendering live in separate modules, so that raising or catching an error does not load `rich`, and that the renderer does not merge into `console.py`. Verify: the filename carries the next number, and the record cites no change name.

## 2. The move

- [ ] 2.1 Create `poop/report.py` with the rendering moved unchanged from `poop/errors.py`: `_LINE_BREAK`, `_PY_SYNTAX`, `_error_location`, `_quoted`, `_column_width`, `_display_width`, `_caret_column`, `_line_gutter`, `_caret_gutter`, `_CODE`, `_error_segments`, `format_error`, `_styled`, `render_error` and `report`, with a module docstring. Remove them, and the imports only they used, from `errors.py`. Point `cli.py`, `repl.py` and `tests/test_repl.py` at `poop.report`. Move the rendering tests from `tests/test_errors.py` to `tests/test_report.py`, which means every test of `format_error`, `render_error`, `report`, `_caret_column` and `_display_width`. The `describe_chain` and exit-code tests stay. Commit it all as one. Verify: `git grep -nE "from poop.errors import[^\n]*(format_error|render_error|report|_caret_column|_display_width)" -- poop tests` and a multi-line check of the parenthesised imports both find nothing; `uv run pytest tests/test_errors.py tests/test_report.py tests/test_cli.py tests/test_repl.py` exits 0 with its summary line read; the number of tests across `test_errors.py` and `test_report.py` equals the 26 that `test_errors.py` held before the move.
- [ ] 2.2 Add a test to `tests/test_report.py` that runs `sys.executable -I -c "import poop, sys; …"` in a subprocess and asserts that no module named `rich` or `rich.*` is loaded. Verify: the test passes. It fails when run against the parent commit of 2.1, which shows that it detects the coupling (check with `git stash`-free means: run it from a `git worktree` of that commit, then remove the worktree).

## 3. Integration

- [ ] 3.1 Run the full gate: `uv run pytest` (95% floor, summary line read), `uv run ruff check`, `uv run ruff format --check` and `uv run ty check poop/ tests/`. Run `printf 'print(1)\n' | uv run poop -` and `uv run poop examples/basics/hello_world.py`. Verify: every command exits as expected (0 for the gate and the example, 3 for the refused program), and the refused program prints its source line and caret on stderr.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*).
