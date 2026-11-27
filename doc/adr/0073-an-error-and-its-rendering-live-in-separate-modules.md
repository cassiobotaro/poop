# 73. An error and its rendering live in separate modules

Date: 2026-11-27

## Status

Accepted

## Context

`poop/errors.py` held the exception classes and also their rendering for a terminal: the gutter, the caret, the display width and the coloured form. Every module that raises or catches a POOP error imports `errors.py`. The parser, the executor, the interpreter and every validator do, so `import poop` loaded `rich`, although only `cli.py` and `repl.py` print an error.

`PoopError` already declares every attribute the rendering reads: `message`, `lineno`, `col_offset` and `chain`.

## Decision

We will keep the exception classes and `ExitCode` in `poop/errors.py` and move the rendering to `poop/report.py`. `cli.py` and `repl.py` import `report` from there, and no other module does.

The rendering does not go into `poop/console.py`. `console.py` holds the two streams and the colour decision, and the REPL also prints values through it. The rendering depends on `console.py`, and `console.py` does not depend on the rendering.

## Consequences

Raising or catching a POOP error no longer loads `rich`, and a test checks that `import poop` loads no `rich` module.

`format_error`, `render_error` and `report` are no longer importable from `poop.errors`. No re-export is kept there, because it would keep `rich` loaded by `errors.py`.
