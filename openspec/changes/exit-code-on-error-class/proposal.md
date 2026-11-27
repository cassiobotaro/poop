# Proposal

## Why

`poop/cli.py` maps an error to its exit code with `EXIT_CODES[type(exc)]`, a
dict keyed by the exact class. The lookup works today only because no class
derives from `ParseError`, `ValidationError`, `TransformError` or
`ExecutionError`. The first subclass would raise `KeyError` inside
`_poop_errors`, the handler that exists to turn a failure into a clean exit.
The codes themselves are bare integers: `UNREADABLE = 1` is named, and the
others are literals in the table, with their meaning in a comment.

## What Changes

- **Each `PoopError` subclass carries its exit code** as a class attribute,
  `exit_code: ClassVar[ExitCode]`. A subclass inherits its parent's code, so
  a `ValidationError` subclass exits 3 like its parent. `cli.py` reads
  `exc.exit_code`, and the `EXIT_CODES` table and the `exit_code()` function
  are removed.
- **The codes become an `IntEnum`, `ExitCode`**, in `poop/errors.py`:
  `UNREADABLE = 1`, `NOT_A_PROGRAM = 2`, `REFUSED = 3` and `FAILED = 4`.
  `NOT_A_PROGRAM` is the code a parse error shares with typer's usage errors,
  and `FAILED` the code a transform error shares with a run-time failure, as
  the comment in `cli.py` already explains. `_unreadable` exits with
  `ExitCode.UNREADABLE`, and the module constant `UNREADABLE` goes away.
- **New ADR**, the next number in `doc/adr/`: the exit code is a property of
  the error class, not a table in the CLI.

No observable behaviour changes. Every failure exits with the code it exits
with today, which the `cli` spec's *Exit codes tell the failure kinds apart*
requirement already pins.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: the codes are unchanged, and `openspec/specs/cli/spec.md` already
     states them. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Edited: `poop/errors.py`, `poop/cli.py`, `tests/test_errors.py`; new
  `doc/adr/NNNN-*.md`.
- `EXIT_CODES`, `exit_code()` and `UNREADABLE` leave `poop.cli`. Nothing
  outside `cli.py` uses them: `git grep` finds no other reference in `poop/`,
  `tests/` or the docs.
- `README.md` and `MIGRATION.md` do not mention exit codes, and they stay
  unchanged.

## Out of scope

- **An `OK = 0` member.** Success never raises, and `typer.Exit()` already
  defaults to 0, so the member would have no reader.
- **Changing any code.** Splitting the codes for transform and usage errors
  away from execution and parse errors would be a behaviour change, and
  scripts may already branch on them.
- **The other items of the review.** Immutable registries and the renderer's
  move out of `errors.py` are separate changes.
