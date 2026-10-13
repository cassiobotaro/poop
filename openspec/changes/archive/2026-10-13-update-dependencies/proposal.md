# Proposal

## Why

Every dependency the project declares is behind its latest release, and the
machinery meant to keep them current cannot run: Dependabot's `uv` updater
supports Python 3.10 through 3.14 only, so against `requires-python = ">=3.15"`
every weekly run has failed since the project moved to 3.15, and its four open
pull requests (#70, #77, #78, #79) are stale snapshots it can no longer rebase.
The toolchain gap matters most: ty has moved 17 releases (0.0.70 to 0.0.87)
and ruff a minor (0.16.2 to 0.17.0), and the newer ty already finds 15
diagnostics in the tree that the pinned one does not.

## What Changes

- **Lock refresh**: `uv lock --upgrade` moves seven packages; the dry run
  shows exactly these:
  - direct: typer 0.27.1 → 0.27.3, prek 0.4.13 → 0.5.5, ruff 0.16.2 → 0.17.0,
    ty 0.0.70 → 0.0.87
  - transitive: coverage 7.15.4 → 7.16.2, iniconfig 2.3.0 → 2.3.1,
    pygments 2.20.0 → 2.21.0
  - unchanged: rich 15.0.0, pytest-cov 7.1.0, pytest 9.1.1 (already latest).
- **Floors follow the lock**: the `>=` minimums in `pyproject.toml` move to
  the locked versions, as `c2e2183` ("raise the floors to what is locked") set
  the convention.
- **The tree passes the new ty**: 15 diagnostics, verified against the
  unchanged tree with `uvx ty@0.0.87`, fixed at their sites (none by
  widening a rule-level ignore):
  - 10 `invalid-mutable-override`: eight `_eq_group`/`_order_group` class
    attributes narrowed from `ClassVar[str | None]` to `ClassVar[str]`, and
    `ValidationError`'s `lineno`/`col_offset` narrowed from `int | None` to
    `int`.
  - 1 `invalid-argument-type`: `Block.__get__` building `partial(self, instance)`
    against the block's `ParamSpec`.
  - 3 `deprecated`: `@contextmanager` functions annotated `-> Iterator[None]`,
    which the current typeshed deprecates in favour of `Generator`.
  - 1 `redundant-condition`: a test asserting a bound method is truthy.
- **ruff 0.17.0 and prek 0.5.5 need nothing**: both were run against the tree
  (`check`, `format --check`, `validate-config`, the `ty` hook) and pass.
- **Dependabot housekeeping**: the four superseded pull requests are closed
  with a comment pointing at this change. The `dependabot.yml` entries stay:
  the GitHub Actions updater works (its last run succeeded, `checkout@v7` and
  `setup-uv@v7` are current), and the `uv` updater resumes by itself once
  Dependabot adds 3.15.

No behavior of the language changes. No validator, transformer or type is
added; every code edit is an annotation or a test assertion.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: dependency pins, type annotations and one test assertion; no
     spec-level behavior. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- `uv.lock`, `pyproject.toml` (`dependencies`, `dependency-groups.dev`).
- `poop/errors.py`, `poop/types/block.py`, `poop/types/_mapping.py`,
  `poop/types/bytes.py`, `poop/types/byte_array.py`, `poop/types/frozen_set.py`,
  `poop/types/memory_view.py`, `poop/types/set.py` (annotations only).
- `poop/cli.py`, `poop/executor.py`, `poop/repl.py` (return annotation of one
  context manager each).
- `tests/test_types/test_sentinel.py` (one assertion).
- GitHub: pull requests #70, #77, #78, #79 closed.
- CI: the 3.15 and 3.15t jobs install the new lock; the hooks (`prek`) run the
  new ruff and ty.
