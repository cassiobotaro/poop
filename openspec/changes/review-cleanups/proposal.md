# Proposal

## Why

Three small findings from a review of the package. One of them is worth a
change:

- `executor._describe` only returns `describe(exc)` (`poop/types/exceptions.py`).
  It adds a frame on every reported failure and a second name for one
  function. Its 15-line docstring explains reasoning that belongs to
  `describe`, and four comments point readers at the alias.

## What Changes

- **`_describe` is removed.** `execute` calls `describe` directly. The part
  of `_describe`'s docstring that `describe`'s own docstring does not already
  say, namely why `str(exc)` alone is not enough, moves there. The comments
  that name `_describe` (`executor.py`, `types/_message.py`, `types/error.py`,
  `tests/test_no_python_wording.py`, `tests/test_types/test_iterator_base.py`)
  name `describe` instead.

No behaviour of the language changes. `describe` is what every report already
goes through.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: internal refactors. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Edited: `poop/executor.py`, `poop/types/exceptions.py`,
  `poop/types/_message.py`, `poop/types/error.py`,
  `tests/test_no_python_wording.py`, `tests/test_types/test_iterator_base.py`.
- No ADR. Removing an alias makes no decision.

## Out of scope

The other findings are left as they are after a closer look:

- **A native `TypeError` from `BaseTransformer.__init_subclass__`.** It was
  implemented and reverted. `tests/test_mirrored_raises.py` requires every
  `raise` in `poop/types` and `poop/transformers` to use a mirror, with
  exemptions listed by function name. Exempting `__init_subclass__` would
  also exempt `Object.__init_subclass__`, which a program's classes reach,
  and moving the check into a named helper only to exempt it would bend the
  code to the test. The mirror stays, as the sweep intends.
- **Renaming `BINDINGS` to `bindings`.** Upper case is the usual spelling for
  a class-level constant, and `BINDINGS` is one: a dict fixed at class
  definition. `rewriter` is a class, read as a type. The rename would touch
  about 60 files, all of the transformers and their tests, and fix nothing.
- **Merging `run_source` and `run_source_repl`.** Each is two lines, transform
  then execute. The names say which of the two modes a caller wants, and the
  REPL one carries the comment on per-input filenames. A merged method would
  turn the name into a `mode=` argument and save no code.
