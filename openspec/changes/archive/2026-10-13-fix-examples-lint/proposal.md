# Proposal

## Why

CI on `main` has been red since the push after `53ec065` ("turn on the rules
the code already passes"): `uv run ruff check` finds 21 errors, all in
`examples/`, which the pre-commit hooks never re-lint because they only see
staged files. A red pipeline hides every real failure that follows it, and the
findings themselves are not defects — they are the shape of a POOP program.

## What Changes

- `pyproject.toml`: the `examples/**/*.py` entry of
  `[tool.ruff.lint.per-file-ignores]` gains two rules, each with its reason:
  - `PLW0108` (19 sites): a `lambda` *is* POOP's block literal, the twin of
    Smalltalk's `[...]`. Ruff's fix would rewrite `lambda: "Fizz".print()` as
    `"Fizz".print`, the bare-method spelling `INFECTIONS.md` keeps unidiomatic
    on purpose.
  - `ARG005` (1 site): `With(...).do(lambda c: 1 / 0)` ignores the manager it
    is handed, which is the point of the example (a body that fails).
- `examples/patterns/money.py`: the one `PIE808` site, `range(0, parts)`,
  becomes `range(parts)`, the Python idiom POOP mirrors everywhere else. The
  Smalltalk twin in the docstring keeps `(0 to: n - 1)`; `range(parts)` is how
  Python spells the same sequence.
- `CONTRIBUTING.md`: the Testing bullet that says `examples/` is excluded from
  `ty` and from `F821` is extended to name every exemption and the one reason
  behind them, so the next rule promotion has a place to look.
- No other example changes. No new validator, transformer or type.

Not in scope: making the hooks lint the whole tree. `prek` passes staged files
by design, and CI already runs the full `ruff check`; the fix is to make CI
green, not to duplicate it locally.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: lint configuration and a contributor note; no spec-level behavior
     changes. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- `pyproject.toml` (`[tool.ruff.lint.per-file-ignores]`, the `examples/**/*.py`
  entry).
- `examples/patterns/money.py` (one line in `allocate`).
- `CONTRIBUTING.md` (Testing section, one bullet).
- CI: `uv run ruff check` returns to exit 0 on `main`; the 3.15 and 3.15t
  jobs stop failing at the lint step.
- `tests/test_doc_counts.py` is unaffected: no example is added or removed.
