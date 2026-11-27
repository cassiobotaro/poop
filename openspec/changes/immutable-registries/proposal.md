# Proposal

## Why

The three registries every interpreter starts from are mutable module globals:

- `DEFAULT_VALIDATORS` (`poop/validators/__init__.py`) is a `list`.
- `DEFAULT_TRANSFORMERS` and `_TRANSFORMER_CLASSES` (`poop/transformers/_registry.py`) are lists too.
- `DEFAULT_NAMESPACE` is a `dict`.

Nothing in the package mutates them. Because they could be mutated,
`Interpreter.__init__` copies the two lists, so that one interpreter's
`append` does not rewrite the registry of every interpreter built after it.
The copy protects the registry, but `Interpreter.validators` then hands out
that interpreter's own list. `tests/test_interpreter.py` clears it from the
outside with `Interpreter().validators.clear()`, so the leak the copy closed
for the registry is open one level down, for the instance.

## What Changes

- **The registries are immutable.** `DEFAULT_VALIDATORS`,
  `DEFAULT_TRANSFORMERS` and `_TRANSFORMER_CLASSES` become tuples, and
  `DEFAULT_NAMESPACE` becomes a read-only `types.MappingProxyType`, annotated
  `Mapping[str, object]`.
- **`Interpreter` keeps tuples and hands out tuples.** It accepts any
  `Sequence` of validators or transformers, stores `tuple(...)` of it, and
  `Interpreter.validators` answers that tuple. It accepts any
  `Mapping[str, object]` as its namespace, and `new_namespace()` still
  answers a fresh `dict` per program.
- **The test that cleared the list** now checks that `validators` answers a
  tuple, and that changing the list an interpreter was built from leaves the
  interpreter's validators unchanged.
- **New ADR**, the next number in `doc/adr/`: the default registries are
  immutable, and the interpreter holds its own immutable copy.
- `.github/copilot-instructions.md` calls the registries "registered lists".
  That word changes to "tuples".

No language behaviour changes. A program runs, validates and reports exactly
as it does today.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none: Python-level API of the interpreter, no spec-level behaviour of
     the language or the CLI. `.openspec.yaml` declares `skip_specs: true`. -->

## Impact

- Edited: `poop/validators/__init__.py`, `poop/transformers/_registry.py`,
  `poop/interpreter.py`, `tests/test_interpreter.py`,
  `.github/copilot-instructions.md`; new `doc/adr/NNNN-*.md`.
- **BREAKING (Python API):** `Interpreter.validators` answers a `tuple`, not a
  `list`, and `DEFAULT_*` can no longer be appended to or assigned into. No
  caller in `poop/` or `tests/` mutates any of them. `repl.py` only reads
  `interpreter.validators`, and `executor.py` only ever receives the `dict`
  that `new_namespace()` builds.
- `CONTRIBUTING.md` says to register a validator *in* `DEFAULT_VALIDATORS` and
  a transformer in `_TRANSFORMER_CLASSES`. That is still true of a tuple
  literal, so it stays unchanged. `README.md` and `MIGRATION.md` do not
  mention the registries.

## Out of scope

- **Freezing the values inside the namespace.** The proxy stops a key from
  being rebound in the registry. The classes it holds stay as they are, and
  their mutability is guarded at run time by `PoopMeta`.
- **Copying a namespace a caller passes in.** `new_namespace()` already copies
  per program, which is the copy that matters.
- **Bringing `.github/copilot-instructions.md` up to date.** It describes
  helpers that no longer exist. Only the word this change makes false is
  touched.
