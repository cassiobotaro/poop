# Design

## Context

See proposal.md — Why. The shapes the additions follow:

- `Boolean.if_true_if_false(t, f)` checks both blocks through `a_block`
  before running one; `Object.if_none` checks its block on the receiver
  that does not run it, so a wrong argument is reported whatever the value.
- `next`, `min` and `max` take a keyword-only `default` with an overload
  pair (`D` present or `MISSING`).
- `explain` in `_selectors.py` tries `SMALLTALK_SELECTORS` (requires the
  mapped name to be a message the receiver has), then
  `CROSS_LANGUAGE_HINTS` keyed by `(builtin name, selector)` down the MRO,
  then `difflib`. The Smalltalk row's hint is composed as `Smalltalk's #X is
  #Y here`.

## Goals / Non-Goals

**Goals:**
- The paired null test and `find`'s default read exactly like their
  siblings (`if_true_if_false`, `next(default=…)`).
- Every new hint is pinned by a test and reachable from the REPL.

**Non-Goals:**
- New collection messages beyond `find`'s default; new names on `Int`.

## Decisions

- **`if_none_if_not_none` lives on `Object`, `NoneClass` and `PoopMeta`**,
  each checking both blocks through `a_block` with `param=""` and
  `param="x"` so the arity sentence spells the two lambdas. `Object` runs
  the second with `self`; `NoneClass` runs the first; the class side
  mirrors `Object`. `ifNilIfNotNil` joins `SMALLTALK_SELECTORS`.
- **`find(block, *, default=MISSING)`**: the overload pair of `next`;
  a positional second argument is refused by a sentence naming `default=`,
  composed where `a_block` reports today, so the helper's role text is
  reused.
- **Smalltalk rows carry a message or a spelling**: the table's value
  becomes `str`, and `explain` treats a value starting with `#`-less
  `.`/`range` text as a spelling (no `hasattr` check) and a bare name as a
  message (`hasattr` check kept). One table, two kinds of row; the
  docstring states the rule. Alternative: a second table for spellings —
  rejected, the lookup order would then need a tie-break.
- **Lazy-view rows** go in `CROSS_LANGUAGE_HINTS` keyed by `("map", "len")`
  etc.; the receiver's cloaked name is `map`/`filter`/`zip`/`enumerate`, so
  the MRO walk already matches. The hint text names the receiver's kind
  from the key so one sentence template serves all four.

## Risks / Trade-offs

- [A spelling row for `first` shadows a user class that defines `first`]
  → `explain` only runs after lookup failed; a class that answers `first`
  never reaches it.
- [`find(block, default)` positional today raises `a_block`'s sentence
  about the *second* argument] → the new sentence is explicit about
  `default=`; the old one is not pinned by any test.
