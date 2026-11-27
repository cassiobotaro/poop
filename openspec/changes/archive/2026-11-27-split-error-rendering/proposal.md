# Proposal

## Why

`poop/errors.py` holds two things: the exception hierarchy (`PoopError` and its
four subclasses, and `ExitCode`) and the terminal rendering of those errors
(`format_error`, `render_error`, `report`, and the gutter, caret and
display-width helpers they share). Every module that raises or catches a POOP
error therefore imports `rich`, `unicodedata` and the caret arithmetic. The
parser, the executor, the interpreter and every validator do, and none of them
prints anything. `python -I -c "import poop"` loads `rich` today, although only
the two front ends, `cli.py` and `repl.py`, render an error.

## What Changes

- **New module `poop/report.py`** with the rendering, moved unchanged from
  `errors.py`: `format_error`, `render_error`, `report`, and the private
  helpers `_error_location`, `_error_segments`, `_quoted`, `_column_width`,
  `_display_width`, `_caret_column`, `_line_gutter`, `_caret_gutter`,
  `_styled`, `_LINE_BREAK`, `_PY_SYNTAX` and `_CODE`.
- **`poop/errors.py` keeps the exception classes and `ExitCode`.** It no
  longer imports `rich`, `re`, `unicodedata`, `itertools` or `poop.console`.
- **`cli.py` and `repl.py` import `report` from `poop.report`.**
- **The rendering tests move** from `tests/test_errors.py` to a new
  `tests/test_report.py`. A new test pins the goal: importing `poop` loads no
  `rich` module.
- **New ADR**, the next number in `doc/adr/`: an error and its rendering live
  in separate modules.

No behaviour changes. Every report keeps its wording and layout, and every
moved test passes unchanged except for its import line.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: a module boundary only; no spec-level behaviour.
     `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- New: `poop/report.py`, `tests/test_report.py`, `doc/adr/NNNN-*.md`.
- Edited: `poop/errors.py`, `poop/cli.py`, `poop/repl.py`,
  `tests/test_errors.py`, `tests/test_repl.py` (it imports `report`).
- `poop.errors.format_error`, `render_error` and `report` move. `poop/__init__.py`
  exports only the exception classes, and no doc names the old location (the
  archived changes are history), so nothing outside `poop/` and `tests/`
  follows.
- `README.md` and `MIGRATION.md` do not mention the module, and they stay
  unchanged.

## Out of scope

- **A compatibility re-export in `errors.py`.** The names are internal to the
  package. A re-export would keep `rich` loaded by `errors.py`, which is the
  coupling this change removes.
- **Merging the rendering into `console.py`.** `console.py` decides where text
  goes and whether it is coloured, and the renderer decides what an error looks
  like. Design decision 1 says why they stay apart.
- **Changing the rendering.** The wording, the gutter, the caret and the chain
  layout are unchanged.
