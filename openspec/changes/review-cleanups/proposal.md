# Proposal

## Why

Three small findings from a review of the package. Two of them are worth a
change:

- `executor._describe` only returns `describe(exc)` (`poop/types/exceptions.py`).
  It adds a frame on every reported failure and a second name for one
  function. Its 15-line docstring explains reasoning that belongs to
  `describe`, and four comments point readers at the alias.
- `BaseTransformer.__init_subclass__` (`poop/transformers/base.py`) raises
  `mirrors.TypeError`, POOP's user-facing mirror, when a contributor defines a
  transformer with no `rewriter`. The rule in `poop/types/exceptions.py`
  sends through the mirrors only "a failure a program can reach". A program
  cannot define a transformer, so this is a developer error. `CollectingValidator`
  raises the native `TypeError` for the same mistake. The mirror is also the
  module's only reason to import `poop.types`.

## What Changes

- **`_describe` is removed.** `execute` calls `describe` directly. The part
  of `_describe`'s docstring that `describe`'s own docstring does not already
  say, namely why `str(exc)` alone is not enough, moves there. The comments
  that name `_describe` (`executor.py`, `types/_message.py`, `types/error.py`,
  `tests/test_no_python_wording.py`, `tests/test_types/test_iterator_base.py`)
  name `describe` instead.
- **`BaseTransformer` raises the native `TypeError`**, as `CollectingValidator`
  does, and `transformers/base.py` drops its `poop.types.mirrors` import.
  `tests/test_transformers/test_base.py` asserts that the class raised is
  exactly `TypeError`.

No behaviour of the language changes. `describe` is what every report already
goes through, and no program can reach the transformer check.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: internal refactors. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Edited: `poop/executor.py`, `poop/types/exceptions.py`,
  `poop/types/_message.py`, `poop/types/error.py`,
  `poop/transformers/base.py`, `tests/test_no_python_wording.py`,
  `tests/test_types/test_iterator_base.py`,
  `tests/test_transformers/test_base.py`.
- No ADR. Neither item makes a new decision. The first removes an alias, and
  the second applies the rule `exceptions.py` already states.

## Out of scope

The third finding, and one half of the second, are left as they are after a
closer look:

- **Renaming `BINDINGS` to `bindings`.** Upper case is the usual spelling for
  a class-level constant, and `BINDINGS` is one: a dict fixed at class
  definition. `rewriter` is a class, read as a type. The rename would touch
  about 60 files, all of the transformers and their tests, and fix nothing.
- **Merging `run_source` and `run_source_repl`.** Each is two lines, transform
  then execute. The names say which of the two modes a caller wants, and the
  REPL one carries the comment on per-input filenames. A merged method would
  turn the name into a `mode=` argument and save no code.
