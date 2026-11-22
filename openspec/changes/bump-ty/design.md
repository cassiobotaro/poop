# Design

## Context

See proposal.md — Why. The hooks run `uv run ty check poop/ tests/` on every
commit with the locked `ty`, so each commit of this change has to pass under
the `ty` that is locked when it lands: the source fixes under 0.0.87, the
bump under 0.0.107.

What each release introduced, bisected against the tree at `3374de4c`
(`uvx ty@<version> check poop/ tests/`):

| First seen | Diagnostic | Site |
|---|---|---|
| ≤ 0.0.101 | `invalid-argument-type` on `reduce` | `poop/types/_iterable_mixin.py:179` |
| ≤ 0.0.101 | `missing-union-attribute` | `tests/test_types/test_meta.py:65` |
| ≤ 0.0.101 | three rules renamed (`incompatible-method-override`, `missing-attribute`, `incompatible-mutable-override`) | `pyproject.toml`, `poop/errors.py` |
| 0.0.106 | `invalid-argument-type` on `class_side` and `class_side_refusal` | `poop/types/exceptions.py:55`, `poop/types/meta.py:587` |
| 0.0.107 | two rules renamed (`invalid-explicit-return`, `not-callable`) | `tests/test_types/test_block.py`, `tests/test_types/test_meta.py` |

All five fixes below were applied to a copy of the tree in the scratchpad:
0.0.107 answers `All checks passed!` there, ruff 0.17.6 is clean, and
`tests/test_types` passes (3064 tests). The three source fixes alone, with
no rename, also pass under 0.0.87.

## Goals / Non-Goals

**Goals:**

- `ty` 0.0.107 clean on `poop/` and `tests/`, with no new `ty: ignore`.
- Every commit passes the hooks under the `ty` locked at that commit.

**Non-Goals:**

- Turning on rules that 0.0.107 ships off by default.
- Revisiting the 49 existing `ty: ignore[invalid-argument-type]` comments;
  none of them is reported as unused or renamed.

## Decisions

- **`raise_` takes `cls` positionally (`def raise_(cls, /, *args, **kwargs)`),
  rather than a `ty: ignore`.** The diagnostic is correct. `_Message.__call__`
  is `(self, cls: C, /, *args: P.args, **kwargs: P.kwargs)`, so with
  `**kwargs: object` in `P` a caller may pass `cls=` by keyword; a function
  whose first parameter is positional-or-keyword then gets two values for
  it. A minimal reproduction shows the error only when `*args: object` and
  `**kwargs: object` are both present and the receiver is not
  positional-only, whatever the return type. The same thing happens at run
  time today: `Tagged.raise_(cls="x")` answers `Tagged.raise_() got multiple
  values for argument 'cls'`. The two `raise_` are the only class-side
  messages taking `**kwargs`, so the fix is two characters twice, not a
  sweep. `class_side.__get__` already binds the class positionally.
- **`sum` binds the result to `Any` before returning it**, rather than
  rewriting the fold as a loop or ignoring the diagnostic. `total` is
  already `Any` on purpose (the comment above it: `Object` declares no `+`
  for a checker to follow). The return annotation `Object` is what now
  drives `reduce`'s type variable, and `operator.add` has no overload over
  `Object`. Binding the answer to a name annotated `Any` puts the solver
  back on `total`. The loop (`total = total + item`) also passes, but it
  replaces a line whose comment explains why it is `operator.add` and not
  `+=`; the binding keeps that line and its reasoning intact. ruff's
  `RET504` does not flag an annotated assignment (checked).
- **The test narrows; the override is not widened.** `superclass()` answers
  `PoopMeta | NoneClass`. Holding the answer in a name lets `assert
  superclass is _Animal` narrow it for the `name()` that follows, and the
  test sends `superclass` once instead of twice. Adding
  `missing-union-attribute = "ignore"` to the `tests/**` override also
  passes, but that override is documented as covering the two rules a
  loosely typed block trips, and this site is not a block.
- **Renames land with the bump, in one commit.** 0.0.87 does not know the
  new names and 0.0.107 warns on the old ones, so the lock and the names
  cannot be split without one of the two commits failing the hook. The two
  `type: ignore[unresolved-attribute]` comments in the suite are not
  reported by either version (the rule is off under `tests/**`), but they
  name a rule that no longer exists; they are renamed in the same commit so
  a search for the old names comes back empty.
- **The behaviour fix lands first, as its own commit, with a spec delta.**
  It changes what a program observes, so it gets the `class-side`
  requirement, two tests and the `INFECTIONS.md` sentence, and it is not
  buried in a `chore(deps)` commit.

## Risks / Trade-offs

- [A program relied on `cls=` being refused] → Not a supported spelling:
  the refusal named an internal parameter and no test, example or doc
  mentions it. The keyword now does what every other keyword does.
- [0.0.108 lands mid-change] → The target is pinned by version in the
  tasks (`uv lock --upgrade-package ty==0.0.107`); a newer release is the
  next bump, tested first as this one was.
- [The free-threaded job] → `ty` is a dev tool with no import at run time;
  the source fixes are signature and annotation changes. CI's `3.15t` job
  is still the check, since no free-threaded build is installed locally.
