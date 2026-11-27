# Design

## Context

See proposal.md, *Why*. The decision itself, that an error and its rendering
live in separate modules, is recorded in the new ADR (task 1.1). This document
keeps only what is specific to the change.

`report` reads three attributes off an error, `message`, `lineno` and
`col_offset`, plus `chain` and `__str__`. `PoopError` already declares all of
them so that the renderer reads attributes and does not probe subclasses.
That interface is what lets the renderer move without changing either side.

## Goals / Non-Goals

**Goals:**
- `import poop`, and any module that only raises or catches a POOP error,
  loads no `rich`.

**Non-Goals:**
- Lazy-importing `rich` inside the renderer. The renderer is only imported
  by the two front ends, which need `rich` anyway.

## Decisions

1. **`poop/report.py`, not `poop/console.py`.** `console.py` is the two
   streams and the colour decision (`OUT`, `ERR`, `in_colour`, `error_line`),
   and the REPL writes values through it as well as errors. The renderer
   depends on it (`report` calls `error_line` and `in_colour`), not the other
   way round. Merging the two would give the value-printing path a dependency
   on the caret arithmetic. The module is named for its public function,
   `report`, which both front ends call.
2. **One commit for the move.** The functions leave `errors.py` and arrive in
   `report.py` in the same commit, together with the import changes and the
   moved tests, so no commit has two copies or a broken import.
3. **The import test runs in a subprocess with `-I`.** The test process has
   already imported `rich` through pytest's plugins and `tests/_support`, so
   `sys.modules` there proves nothing. A fresh interpreter importing `poop`
   alone does.

## Risks / Trade-offs

- **[A test imports a moved private helper]** → `_caret_column` and
  `_display_width` are imported by `tests/test_errors.py` only, and they move
  with the tests to `tests/test_report.py`. Task 2.1 checks with `git grep`
  that no other file imports them from `poop.errors`.
- **[Something else on the import path loads `rich`]** → Measured before the
  change: `import poop` loads `rich` only through `poop.errors`.
  `poop/types/_message.py` matches `git grep rich` only for the word "richer".
  If the new test fails after the move, the failure names the importer, and it
  is fixed or the goal is revised before task 2.2 is ticked.
