# Proposal

## Why

The wording sweep in `tests/test_no_python_wording.py` sends every public
message on every wrapper with wrong-typed arguments and refuses CPython's
phrasing in what comes back; its `_receivers()` docstring promises "one live
value per wrapper". It holds seventeen. Building the samples the sweep lacks
and running it shows the gap: `MemoryView`, `MappingProxy`, the three dict
views, every iterator, `Map`, `Filter`, `Enumerate`, `Zip`, `Block`,
`EllipsisClass` and `Error` have never been swept — fifteen receivers,
about 560 message sends, that a leak could hide behind today. (Run on the
current tree, the fifteen are clean; the point is that nothing would say so
if they were not.)

## What Changes

- **Samples for every unsampled wrapper** in `_receivers()`: a `MemoryView`
  over `bytes` and one over a `bytearray` (the two answer `hash` and
  `readonly` differently), a `MappingProxy`, `dict_keys`/`dict_values`/
  `dict_items`, one iterator of each kind the language hands out (`list`,
  `tuple`, `str`, `bytes`, `bytearray`, `memoryview`, `set`, `frozenset`,
  `range`, and the four dict iterators plus their three reversed twins), an
  `Enumerate`, a `Zip`, a `Map`, a `Filter`, a `Block`, the `ellipsis` and an
  `Error` wrapping a mirrored exception.
- **A guard that the sample list stays complete**: a test walking every
  class under `poop.types` that is a wrapper a program can hold (a
  `PoopMeta` class, not an alias, not private) and asserting the sweep has a
  sample whose type is that class or a subclass. The exemptions are named in
  the test with a reason each: `Try` and `With` (their messages run the
  blocks they hold, and their refusals are pinned in `test_try_.py` and
  `test_with_.py`), and the exception mirrors (classes a program raises or
  catches, met at runtime only through `Error`, which is sampled).
- **`INFECTIONS.md`**: the Principles bullet on the mechanical sweep says
  the receiver list covers every wrapper and is itself checked.

No spec-level behavior changes: no message answers anything new and no
refusal is reworded, which is why this change declares `skip_specs`. If the
sweep over a new sample surfaces a leak while implementing, that leak is a
finding for a change of its own, under the type it belongs to, not a silent
fix here.

Out of scope, and why: `Try` and `With` as sweep receivers (above);
widening `_wrong_arguments()` with more shapes (a separate question about
the sweep's probes, not its receivers); the exception mirror classes as
receivers (a program meets an exception as an `Error`, never as the raw
mirror).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — test infrastructure only; `skip_specs: true`)

## Impact

- `tests/test_no_python_wording.py` (`_receivers()`, one new test, the
  comment block above the sweep).
- `INFECTIONS.md` (one sentence in the Principles bullet on the sweep).
- No change under `poop/`. `README.md` counts are unchanged.
