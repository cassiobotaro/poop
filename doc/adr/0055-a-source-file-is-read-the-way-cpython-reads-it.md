# 55. A source file is read the way CPython reads it

Date: 2026-08-11

## Status

Accepted

## Context

An ordinary file was mishandled in two ways.

A byte-order mark, which editors on Windows write by default, survived `encoding="utf-8"` as a literal `U+FEFF`, and the tokenizer refused a file `python3` runs, naming a character invisible in every editor. `utf-8-sig` is what CPython's own loader uses. The REPL's stdin path reads through `input()`, which does not strip the mark.

The caret under a reported line counted characters, so a tab, one character and eight columns, put it in the indentation of every tab-indented file, further off the deeper the nesting. `_caret_column` already existed for this class of bug (bytes versus characters).

## Decision

POOP reads and reports a program's own file as CPython does (`poop/cli.py`, `poop/interpreter.py`, `poop/repl.py`, `poop/errors.py`).

- A file is read as `utf-8-sig`, and the REPL's stdin path spends the mark once, on the first line.
- The quoted line in a report is `expandtabs()`-ed, and the caret is measured over the same expansion.

## Consequences

A file with a byte-order mark runs under POOP as it does under `python3`.

The caret lands under the reported column in a tab-indented file. Expanding the tabs also keeps the terminal's own tab stops out of the measure, since those start at the gutter, not at the file's column 0.
