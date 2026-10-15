# Proposal

## Why

Three places where a POOP program cannot say what it means, found while
probing the collection and null protocols: the two-branch null test cannot
be written (`x.if_not_none(…).if_none(…)` runs the second block on the
first block's *answer*, so a branch that legitimately answers `none` fires
the other), `find` cannot tell "nothing matched" from "matched `None`", and
the near-miss hints know seventeen Smalltalk selectors but not `first`,
`isEmpty`, `detect:ifNone:` or `timesRepeat:`, and say nothing useful when a
lazy `map` is sent `len`.

## What Changes

- **`if_none_if_not_none(none_block, present_block)`** on every object, on
  `none` and on the class side — the paired form `Boolean` already has as
  `if_true_if_false`, and Smalltalk's `ifNil:ifNotNil:`. `if_not_none_if_none`
  is its twin, as `if_false_if_true` is.
- **`find(block, default=…)`**: a keyword-only `default` answered on a miss,
  the shape `next`, `min` and `max` already take.
- **Near-miss hints grow**: the Smalltalk table gains `first`, `last`,
  `isEmpty`, `notEmpty`, `add`, `addAll`, `removeFirst`, `removeLast`,
  `copyFrom`, `at:ifAbsent:` (`atIfAbsent`), `atIfAbsentPut`, `removeKey`,
  `keysAndValuesDo`, `anySatisfy`, `allSatisfy`, `detectIfNone`,
  `asArray`, `asSet`, `timesRepeat`, `toDo`, `ifNilIfNotNil`; a row may
  carry a *spelling* (`#first is .at(0) here`) where the twin is not a
  message name. The lazy views (`map`, `filter`, `zip`, `enumerate`) gain
  cross-language rows for `len`, `at`, `reversed`, `includes`, `count`,
  `index` pointing at materialising with `list(...)` (`sorted` the views
  already answer, through the mixin).

Out of scope, and why: `times_repeat`/`to_do` as messages — `INFECTIONS.md`'s
"Python names" principle makes `range(n).do(…)` the spelling, so they are
hints, not messages; `all`/`any` without a block, a deliberate choice the
review confirmed; `@x.setter`, a class-definition allowance that is not a
collection gap and deserves its own proposal; `xs.map(f)` printing `<map>`,
which mirrors CPython and is what the new hint explains.

## Capabilities

### New Capabilities

- `none-type`: what `none` answers, including the paired null test.
- `does-not-understand`: the hints a refused message carries.

### Modified Capabilities

- `object-type`: the paired null test on every object.
- `collection-iterable-methods`: `find` with a default.

## Impact

- `poop/types/object.py`, `none.py`, `meta.py` (class side),
  `_iterable_mixin.py`, `_selectors.py`.
- Tests: `tests/test_types/test_object.py`, `test_none.py`, `test_meta.py`,
  the iterable-mixin tests, `tests/test_types/test_selectors.py`.
- Docs: `INFECTIONS.md` (`NoneClass`, `Collection iterable methods`, the
  hints paragraph), `MIGRATION.md` (`x if x is not None else d` row,
  `next((… ), d)` row), `README.md` essentials table unchanged.
