# Design

## Context

See proposal.md - Why. What was observed on the 3.15 toolchain uv resolves
(ruff 0.16.2 from `uv.lock`, the same CI installs):

- `uv run ruff check` on a clean checkout of `main`: 21 errors, 19 `PLW0108`,
  1 `ARG005`, 1 `PIE808`, every one under `examples/`. `poop/` and `tests/`
  are clean. The last CI run on `main` (`38049334745`, the push of `dc28b1a`)
  fails at the lint step with the identical 21.
- They arrived with `53ec065`, which added `PL`, `PIE` and `ARG` to `select`.
  The hooks (`prek`, `.pre-commit-config.yaml`) pass only staged files to
  `ruff check --fix`, so a configuration change never re-lints a file that was
  not itself edited; `examples/` has stayed untouched since.
- `ruff check --diff --unsafe-fixes --select PLW0108` shows the fix ruff
  proposes: `lambda: "Fizz".print()` becomes `"Fizz".print`, and
  `while_true(lambda: self._step())` becomes `while_true(self._step)`.
- `INFECTIONS.md` (Block section, "The other spelling stays a leak, on purpose
  and on a measurement") keeps the bare-method spelling deliberately
  unidiomatic: the language's block literal is `lambda`, and every example's
  Smalltalk twin writes the same thing as `[...]`. `tests/*` already ignores
  `PLW0108` and `ARG005` for the same reason ("wrap a call to spell a block").

## Goals / Non-Goals

**Goals:**
- `uv run ruff check` exits 0 on the whole tree, so CI on `main` is green.
- Every exemption is written down where the next rule promotion will find it.

**Non-Goals:**
- Rewriting examples to satisfy the rules. The rewrite ruff proposes teaches
  the wrong spelling.
- Making the hooks lint the whole tree, or adding a CI step that already
  exists.
- Any change to `poop/` or `tests/`.

## Decisions

**1. Ignore `PLW0108` and `ARG005` for `examples/**/*.py`, next to `F821` and
`ANN`.** A block in POOP is a `lambda`; the rule's "unnecessary lambda" is the
block literal itself, and its fix is the bare-method spelling the catalogue
measures and declines. A block parameter the body ignores (`lambda c: 1 / 0`)
is what `With.do` hands its body by contract.
*Alternative*: apply ruff's unsafe fix. Rejected: `"Fizz".print` runs (the
probe prints) but is exactly the spelling the Block section calls a leak with
no idiomatic use, and the examples exist to teach the idiomatic one.
*Alternative*: `# noqa` on each of the 20 lines. Rejected: twenty comments in
teaching material, for one reason.

**2. Fix the one `PIE808` site instead of ignoring the rule.** `range(0,
parts)` in `money.py` becomes `range(parts)`: POOP mirrors Python's names and
idioms (`map` not `collect`, `reduce` not `inject:into:`), and `range(n)` is
the Python spelling of the twin's `(0 to: n - 1)`. The docstring's Smalltalk
stays as it is; the twin anchors *what* the code says, not how Python spells a
range. The fix is ruff's own safe one, and the example's output is unchanged.
*Alternative*: ignore `PIE808` for `examples/**/*.py`, keeping the explicit
`0` as a visual echo of `0 to:`. Declined by the maintainer: the Python idiom
is the one POOP teaches.

**3. The exemptions are explained in `CONTRIBUTING.md`, not only in
`pyproject.toml`.** The Testing bullet already explains two of them (`ty`,
`F821`); it is the place a contributor reads before touching lint, and the one
sentence that says "examples are POOP programs, not Python modules" covers all
four.

## Risks / Trade-offs

- [A future ruff rule flags another block-shaped construct in `examples/`
  and CI goes red again] → the CONTRIBUTING bullet names the reason, so the
  next entry is a one-line addition with a precedent; CI, not the hooks, is
  the gate that catches it.
- [Ignoring `ARG005` in examples hides a genuinely unused parameter in a
  future example] → the examples are reviewed as teaching text, and an unused
  block parameter is either the `With.do` contract or visible in review.
