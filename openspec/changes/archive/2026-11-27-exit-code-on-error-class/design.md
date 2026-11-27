# Design

## Context

See proposal.md, *Why*. The decision to put the exit code on the error class
rather than in a table in the CLI is recorded in the new ADR (task 1.1). This
document keeps only what is specific to the change.

`_poop_errors` (`poop/cli.py`) catches `PoopError` and raises
`typer.Exit(exit_code(exc))`, and `_validators_only` exits with
`exit_code(errors[0])`. These are the two readers of the table. `typer.Exit`
accepts any `int`, and an `IntEnum` member is one.

## Goals / Non-Goals

**Goals:**
- Any `PoopError` subclass, present or future, has an exit code without
  registering one.

**Non-Goals:**
- Moving the renderer out of `errors.py`. That is a separate change, and
  `ExitCode` lives next to the classes that declare it whichever module the
  renderer ends up in.

## Decisions

1. **`ExitCode` lives in `poop/errors.py`.** The classes there declare their
   codes, so the enum must be defined before them. `cli.py` already imports
   from `errors.py`. Putting the enum in `cli.py` would make `errors.py`
   import the CLI.
2. **`PoopError` declares `exit_code: ClassVar[ExitCode] = ExitCode.FAILED`.**
   The four subclasses override it with their own code. A bare annotation
   with no value on the base would bring back the failure this change
   removes, a missing code found only on the error path, as an
   `AttributeError` instead of a `KeyError`. `FAILED` is the honest default,
   since an error of unknown kind is a failure of the run.
3. **Member names say what the code means to a script, not which class
   raises it.** `NOT_A_PROGRAM` covers a parse error and a usage error, and
   `FAILED` covers a transform error and a run-time failure. The comment
   above the current table already uses those words.

## Risks / Trade-offs

- **[Public names leave `poop.cli`]** → `EXIT_CODES`, `exit_code` and
  `UNREADABLE` have no reader outside the module. Task 2.2 confirms that
  with `git grep` before removing them.
