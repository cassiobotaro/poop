# POOP Backlog

Pending work, open questions, and known inconsistencies. See `INFECTIONS.md` for what is already implemented.

## Validators — awaiting substitute

These validators are not yet active because the POOP substitute does not exist yet.

| Construct | Validator | Pending substitute |
|---|---|---|
| *(none)* | — | — |

## Missing validators

## Python builtins — remaining decisions

| Builtin | Note |
|---|---|
| `sorted(x)` | blocked by `no_sorted` — use `col.sorted()` |
| `super` | needed for inheritance — allow |
| `property` / `classmethod` / `staticmethod` | class definition — allow |

## Architecture / DX

- **REPL**: interactive loop — `poop` with no arguments opens the REPL. Complexity is medium. Skeleton is trivial (Python has `code.InteractiveConsole`), but integrating with the validator/transformer pipeline requires some changes:
  - **Persistent namespace** (blocker): `executor.py` currently copies the namespace on every call (`ns = dict(namespace)`), so variables defined in one input are lost in the next. The executor needs to accept a mutable namespace passed by reference and update it in place.
  - **Multi-line input** (medium): detecting incomplete input (e.g., `class Foo:` without a body). Python's `compile(..., mode='single')` raises `SyntaxError` to distinguish "incomplete" from "invalid", but the POOP pipeline adds validators/transformers in between.
  - **Expression printing** (medium): `compile(mode='exec')` never prints results. `compile(mode='single')` auto-prints expression values — the executor would need a REPL mode that uses `'single'` instead of `'exec'`.
  - **Error recovery** (easy): `ValidationError`, `ParseError`, and `ExecutionError` must be caught and displayed without killing the process.
- **Richer error messages**: `ValidationError` could suggest the POOP equivalent (e.g., `"use x.not_() instead of 'not x'"`).

## Code examples

- Expand `examples/` with collections: `List`, `Tuple`, `Interval` with `map`/`filter`/`filter_false`.

## Open decisions

*(none)*
