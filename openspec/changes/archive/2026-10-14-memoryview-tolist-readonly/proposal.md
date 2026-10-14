# Proposal

## Why

The surface diff behind `text-mirrors-complete` listed sixteen `memoryview`
names missing on `MemoryView`; fourteen were declined in `INFECTIONS.md` as
buffer-protocol vocabulary that would answer constants, and the same paragraph
names `tolist` and `readonly` as "the two with content, left for their own
change". This is that change: a view a program can materialize as a `List`
and ask whether the bytes behind it can change, which is the question the
`hash` refusal already answers in prose.

## What Changes

- **`MemoryView.tolist()`**: a `List` of `Int`, one per byte, as
  `memoryview.tolist` answers for a byte view. Takes no argument; an extra
  one is left to CPython's arity report, as every other message's is.
- **`MemoryView.readonly()`**: a `Boolean`, `true` over `bytes` and `false`
  over `bytearray`, as CPython's `memoryview.readonly` is — spelt as a
  *message*, not an attribute, by the rule that already turned `real`,
  `imag`, `numerator` and `Range.start` into methods ("Python's numeric
  accessors are messages too"). A slice or a reversed view answers what the
  view it came from answers.
- **`INFECTIONS.md`**: the "buffer-protocol attributes stay out" paragraph
  stops deferring the two and says what they answer; two rows in the
  "Builtin-mirroring method signatures" table; the `hash` refusal paragraph
  is unchanged.

Out of scope, and why: the fourteen declined buffer attributes (`shape`,
`strides`, `itemsize`, `format`, `ndim`, `cast`, `toreadonly`, `release`,
`obj`, the contiguity flags), decided in `text-mirrors-complete`; `toreadonly`
in particular, because it would be the only way to *make* a read-only view
and POOP has `bytes(buf)` for that; and adding a `memoryview` sample to the
wording sweep's receiver list in `tests/test_no_python_wording.py`, which is
missing today and is a test-infrastructure finding of its own.

## Capabilities

### New Capabilities
- `memoryview-type`: the messages a `MemoryView` answers, mirroring CPython's
  `memoryview` for one-dimensional byte views in POOP's wording. This change
  adds `tolist` and `readonly`.

### Modified Capabilities

(none)

## Impact

- `poop/types/memory_view.py` (`tolist`, `readonly`).
- Tests: `tests/test_types/test_memory_view.py`.
- Docs: `INFECTIONS.md` (MemoryView paragraph, signature table rows).
  `README.md` counts are unchanged.
