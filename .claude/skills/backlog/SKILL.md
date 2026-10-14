# Backlog Workflow

The backlog is the set of active OpenSpec changes under `openspec/changes/`.
One change per theme, one task per finding.

1. `openspec list` to see the active changes and their task progress. Nothing
   active means the backlog is empty; a new idea starts with `/opsx:propose`.
2. Pick a change with the user. Discuss trade-offs before implementing, and
   confirm scope: which tasks, in which order. They may want only a subset.
3. `/opsx:apply <name>`: work the tasks in atomic commits, ticking each as it
   lands, with `INFECTIONS.md` and `README.md` updated in the same commit as
   the code. Run the full gate before each commit:
   `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`.
4. `/opsx:archive <name>` once every task is done: delta specs sync into
   `openspec/specs/`, the change moves to `openspec/changes/archive/`, and the
   archive is committed as `chore(openspec): archive <name>`.
