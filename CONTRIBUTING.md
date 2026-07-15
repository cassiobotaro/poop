# Contributing to POOP

Thanks for your interest! POOP is a Python interpreter infected by Smalltalk —
the goal is that **every operation looks like a message sent to an object**.

This document is the canonical source for contributor workflow and conventions.
By participating, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting started

POOP requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/cassiobotaro/poop.git
cd poop
uv sync --dev
prek install                        # enable git hooks
uv run pytest                       # run the test suite
uv run poop examples/basics/hello_world.py # run an example
```

The pipeline is `parse → validate → transform → execute(namespace)`. Source files:

- `poop/parser.py` — wraps `ast.parse`
- `poop/validators/` — AST validators that reject forbidden constructs
- `poop/transformers/` — AST transformers that rewrite literals/calls into POOP types
- `poop/types/` — POOP types (`Object` is the root)
- `poop/executor.py` — compiles and executes AST in an injectable namespace
- `poop/interpreter.py` — orchestrates the full pipeline

Reference catalog of validators, transformers, and types:
[`INFECTIONS.md`](INFECTIONS.md). Open backlog: [`proposals.md`](proposals.md).

## Workflow

### Atomic commits

One concern per commit — one validator, one type, one transformer, one bug fix.
Never group unrelated changes.

For multi-part work (e.g. a new validator + a new type + an example), split into
separate commits in dependency order.

### Confirm scope before multi-part plans

Open work that spans more than ~3 files or introduces a public-API change
deserves a quick alignment in `proposals.md` or via an issue. The maintainer may
want only a subset implemented.

### Pre-commit hooks

`prek install` registers the hooks defined in `.pre-commit-config.yaml`. They
run on every commit:

- `ruff check --fix`
- `ruff format`
- `ty check poop/ tests/`

A failed hook means the commit did **not** happen — fix the issue and create a
**new** commit. Do not `--amend` after a hook failure.

## Conventions

### Imports

All imports live at the top of the module. Use a function-local `import` only
to break a circular import. Imports needed exclusively for type annotations go
inside an `if TYPE_CHECKING:` block at the top of the module — never
function-local, never alongside runtime imports.

### Language

- `proposals.md` is written in **English**, regardless of the language used in
  the conversation that produced the entry.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `INFECTIONS.md`, and `README.md` are
  also English.
- Code comments are in English.

### Examples must have a Smalltalk version

Every file in `examples/` must include the equivalent Smalltalk code in its
docstring, like this:

```python
"""
Smalltalk:
    Transcript show: 'Hello, World!'.
"""

"Hello, World!".print()
```

The Smalltalk version anchors the language design — POOP code should look like
its Smalltalk twin.

Place a new example in the subfolder that matches what it teaches:

- `examples/basics/` — language fundamentals (control flow, collections, classes
  with state).
- `examples/idiomatic/` — idiomatic POOP usage (method chaining, null-safe
  cascades, `async`, etc.).
- `examples/patterns/` — Sandi Metz / GoF object-oriented patterns.

### Use the actual current year

License files, copyright notices, dates, and similar references must use the
**actual current year** (not a placeholder, not the year the project started).

### GitHub Actions versions

When editing `.github/workflows/*.yml`, verify each action version is current
(do not pin to a years-old tag without a reason).

## Adding a new validator / transformer / type

Every infection follows the same pattern.

### A new validator (e.g. `no_foo`)

1. Create `poop/validators/no_foo.py`. Reuse `_call_name.make_call_name_validator`
   when forbidding builtin calls; otherwise subclass the base validator.
2. Register it in `DEFAULT_VALIDATORS` (`poop/validators/__init__.py`).
3. Add tests under `tests/test_validators/test_no_foo.py`.
4. Add an entry to `INFECTIONS.md` with a `Substitute` column pointing to the
   POOP equivalent. **Activate a validator only when the substitute exists** —
   blocking without offering an alternative breaks code without teaching.

### A new transformer (e.g. `foo`)

1. Create `poop/transformers/foo.py`.
2. Register it in `DEFAULT_TRANSFORMERS` (`poop/transformers/__init__.py`) and
   inject any helper into `DEFAULT_NAMESPACE`.
3. Add tests under `tests/test_transformers/test_foo.py`.
4. Add an entry to `INFECTIONS.md`.

### A new type (e.g. `Foo`)

1. Create `poop/types/foo.py` inheriting from `Object` (or a relevant mixin).
   Declare `__slots__`. Methods must return POOP types — never bare Python
   values.
2. Wire dunders (`__iter__`, `__add__`, …) to public Python-named methods
   (`iter()`, `__add__` is fine to keep, but new Smalltalk-style behaviour goes
   in a public method).
3. Add tests under `tests/test_types/test_foo.py`.
4. Add an entry to `INFECTIONS.md`.

### Method naming

Methods follow Python names, not Smalltalk names: `map`, not `collect`;
`filter`, not `select`. The exception is `do` (from Smalltalk `do:`) used for
iteration — `for` is a keyword, `for_each` is a Java/JS idiom.

## Closing a proposal

When `proposals.md` item N is implemented:

1. Implement in atomic commits as described above.
2. Either:
   - **Strike + DONE:** rename the heading to `### ~~N. …~~ — DONE` and
     replace the body with a short "Decision + implemented" summary, **or**
   - **Remove:** delete the entry entirely and renumber subsequent items
     sequentially. Update internal cross-references (`#N` mentions elsewhere
     in the file).
3. Update `INFECTIONS.md` if the proposal touched validators, transformers, or
   types.
4. Final commit message: `docs: close proposal N — <one-line decision>`.

## Pull requests

- Branch from `main`. Use a short, lowercase, hyphenated name
  (`feat/iterator-types`, `fix/list-append`).
- Open the PR against `main`. Title under 70 characters; details in the
  description body.
- Required before opening:
  - `uv run pytest` passes
  - `uv run ruff check` and `uv run ruff format` pass
  - `uv run ty check poop/ tests/` passes
  - For UI-facing changes (none today, but in the future): manual smoke test
- The description should explain **why**, not just **what**. The diff already
  shows what.
- Reference the relevant `proposals.md` item if the PR closes one.

## Versioning

The project no longer publishes tagged releases: there are no git tags,
no GitHub Releases, and no release workflow. The `version` field in
`pyproject.toml` is informational — bump it when it makes sense, following
SemVer.

Commit messages still follow [Conventional
Commits](https://www.conventionalcommits.org/), which keeps the git log
readable and maps cleanly onto SemVer intent:

- `fix:` → patch (`1.0.0` → `1.0.1`)
- `feat:` → minor (`1.0.0` → `1.1.0`)
- `feat!:` / `BREAKING CHANGE:` → major (`1.0.0` → `2.0.0`).
- `docs:`, `chore:`, `refactor:`, `test:`, `style:` → no version
  bump.

The git log is the changelog — there is no `CHANGELOG.md` and no
GitHub Releases page.

## Testing

- Tests live next to their target: `poop/types/foo.py` → `tests/test_types/test_foo.py`.
- Verify expected values against actual language semantics before assuming the
  implementation is wrong (e.g. ascii repr quoting, inclusive vs exclusive
  bounds, `__radd__` requirements for `builtins.sum`).
- `examples/` is excluded from `ty` and from ruff `F821` because example files
  rely on names injected at runtime (`True` → POOP boolean, etc.).
- `uv run pytest` enforces a 95% coverage floor (`--cov-fail-under=95` in
  `addopts`) — a run whose tests all pass still exits non-zero below it.
- To measure coverage of a single module in isolation, override the project-wide
  `--cov=poop` from `addopts` and waive the floor for that run:
  `uv run pytest tests/test_types/test_X.py --cov-config=/dev/null --cov=poop.types.X --cov-fail-under=0`.
  The default `addopts` reports a TOTAL percentage averaged across every module
  in `poop`, so a single-file run shows ~48% TOTAL even when the module itself
  is 99% covered — which would trip the floor. `--cov-config=/dev/null` does not
  waive it on its own: the floor lives in pytest's config, not coverage's.

## License

By contributing, you agree your contributions are licensed under the same
license as the project (see `LICENSE`).
