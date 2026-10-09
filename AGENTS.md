# AGENTS.md

POOP is a Python 3.15 interpreter infected by Smalltalk: every operation is a
message sent to an object. [`CONTRIBUTING.md`](CONTRIBUTING.md) is the full
contributor guide and applies to agents as it does to humans. This file holds
only what agents tend to miss.

## Commands

```bash
uv sync --dev && prek install              # setup (uv, not pip; hooks via prek)
uv run pytest                              # tests; 95% coverage floor
uv run pytest tests/test_x.py::test_name   # one test
uv run ruff check --fix && uv run ruff format
uv run ty check poop/ tests/               # examples/ is excluded on purpose
uv run poop examples/basics/hello_world.py # run a program; `poop` alone is the REPL
```

A failed hook means the commit did not happen: fix and create a new commit,
never `--amend`.

## Before you change anything

- Confirm scope with the user before a multi-part plan. They may want a subset
  (e.g. `dir` as a method but `help` as a function).
- New features must be transparent to the end user: lambda transformers,
  `__call__` or syntactic sugar, never an internal name like `Block()`.
- POOP is the language, not the library. No stdlib mirrors, no file I/O, no
  async. Builtins outside `_ALLOWED_BUILTINS` (`poop/executor.py`) answering
  `NameError` is intended. Do not add any of these back without discussion.
- How to add a validator, transformer or type, including why validators
  collect instead of raise and why transformer order matters, is in
  `CONTRIBUTING.md`. Read it before touching `poop/validators/` or
  `poop/transformers/`.

## Names user code can reach

- `DEFAULT_NAMESPACE` (`poop/transformers/_registry.py`) exposes exactly two
  user-facing names, `Try` and `With`. Everything else is a mangled `_poop_*`
  binding reached only through transformer rewrites.
- Injected names keep Python's casing: `Try` and `With` are classes, so
  PascalCase. Wrapper names like `Int` or `List` are never reachable.
- The root class is spelled `object` or `Object`; both rewrite to
  `_poop_object` and both answer `object` to `.name()`.

## Docs

- Update `README.md` and `INFECTIONS.md` in the same commit as the code.
- Run every snippet you add to a doc. `tests/test_doc_counts.py` reads the
  validator and example counts out of `README.md`; keep those sentences in
  shape.
- `proposals.md` is English only. Implemented items are deleted, never
  marked done.
