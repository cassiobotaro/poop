# Proposal

## Why

`no_try` and `no_raise` ban every form of `try` and `raise`, but `Try` and
`raise_` cover only part of them, which breaks the rule that a validator is
active only once its substitute exists. `try … else` has no substitute
(`Try(…).else_` answers `Try does not understand #else_`). `raise X from Y`
has none either, and a caught error cannot be asked for its cause. The
uncaught report shows only the last exception, even though CPython already
chains the one a handler was handling. And `no_try` tells a program that
writes `except*` to use `Try(...).except_(...)`, which does not split an
exception group, while nothing in POOP raises a group in the first place.

## What Changes

- **`Try` answers `else_(block)`**: the block runs only when the protected
  block raised nothing. It receives the protected block's value, and its own
  value becomes what `run()` / `finally_()` answer. A handler never catches
  what it raises, and it runs before the cleanup. It chains like `except_`,
  a non-block is refused where it was written, and a second `else_` is
  refused; a block of the wrong arity is reported when it is called, as
  every block is.
- **An exception instance answers `raise_from(cause)`**:
  `KeyError("outer").raise_from(e)` is `raise KeyError("outer") from e`, and
  `raise_from(None)` is `raise … from None`. The cause may be a caught
  `Error` or a built exception instance.
- **A caught error answers `cause()` and `context()`**: each is the `Error`
  wrapping `__cause__` / `__context__`, or `none` when there is none.
  `context()` also answers `none` when the context was suppressed, the rule
  the report follows too. POOP composes its own failures with
  `raise … from None` while CPython's native exception is still being
  handled, so the raw `__context__` would hand a handler CPython's wording
  (`list index out of range`) for almost every error POOP composes.
- **`raise_` on a built or caught exception refuses arguments in POOP's
  words**: `ValueError("x").raise_(1)` answers CPython's
  `Exception.raise_() takes 1 positional argument but 2 were given` today.
- **The uncaught report shows the chain**: under the `poop: <Kind>: <message>`
  line and its source line, one line per link, `caused by <Kind>: <message>`
  for an explicit cause, or `while handling <Kind>: <message>` for an implicit
  context that was not suppressed. The CLI and the REPL share the report, so
  both show the chain.
- **`except*` becomes a definitive ban**: `no_try` refuses `ast.TryStar` with
  a sentence of its own that points at no substitute, and `INFECTIONS.md`
  lists it next to `async`, the only source of exception groups.

Out of scope, and why:
- **`ExceptionGroup` / `BaseExceptionGroup` mirrors.** POOP mirrors only the
  exceptions it can reach. Nothing in the language raises a group (no async,
  no `TaskGroup`, no threads), so a mirror would exist only for a program
  that builds a group in order to raise it.
- **`suppress_context()` as a message.** Only the printer of a chain reads
  `__suppress_context__`, and both the report and `context()` honour it, so
  there is nothing left for a program to ask.
- **`add_note`, `args`, `with_traceback`** stay refused, as `error-type` and
  `exception-mirrors` already require.
- **A class-side `KeyError.raise_from(…)`.** The class-side `raise_` passes
  its keywords on to the exception's own fields, so a cause keyword would
  take a name away from them. A built instance already answers `raise_()`,
  and `raise_from` follows it.
- **The `Object.print` positional `end` wording leak**
  (`object.print() got multiple values for argument 'end'`). It is a
  separate theme and does not belong to the exception protocol.

## Capabilities

### New Capabilities

- `no-try-validator`: what `no_try` refuses and the sentence it answers for
  each form of `try`, including the definitive ban on `except*`.

### Modified Capabilities

- `try-type`: `Try` gains `else_`, including its ordering against handlers
  and the cleanup, and its refusals.
- `exception-mirrors`: a built exception instance answers `raise_from`, and
  its `raise_` refuses arguments in POOP's words.
- `error-type`: a caught error answers `cause()` and `context()`, and its
  `raise_` refuses arguments in POOP's words.
- `cli`: the uncaught run-time report lists the exception chain under the
  source line.

## Impact

- `poop/types/try_.py` (`else_`, `_execute` ordering).
- `poop/types/exceptions.py` (instance-side `raise_from`, `describe` or a
  sibling for the chain lines).
- `poop/types/error.py` (`cause`, `context`).
- `poop/executor.py`, `poop/errors.py` (`ExecutionError` carries the chain,
  and `format_error` / `render_error` print it after the source line).
- `poop/validators/no_try.py` (the `TryStar` sentence) and `poop/repl.py`
  (an `except*` statement in the `:explain try` snippet).
- `tests/test_no_python_wording.py` coverage for the new refusals.
- `INFECTIONS.md` (*Try*, *Error*, *PoopExcMeta*, *No `try`*, and the
  definitive-ban list in *Principles*). `README.md` shows neither `Try` nor
  a run-time failure, and no validator is added, so its counts stand.
