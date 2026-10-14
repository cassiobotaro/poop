# Proposal

## Why

Python 3.15's `lazy import` (PEP 810) is the spelling the cycles in
`poop/types` always wanted. A module-level `lazy from poop.types.float import
Float` does not run `float.py` until `Float` is first *used*, so a hub that
is needed at class-definition time by the modules it imports can name them
at the top without executing them early — exactly what the 272 function-local
imports under `poop/` do today, one call at a time. Verified on the installed
3.15: the cycle resolves, `vars(module)` reads resolve the name
transparently, PEP 649 annotations that name a lazy import work in
`inspect.signature` and `get_annotations`, and once resolved the name is a
plain module global (30 ns) against 70 ns for the `late()` getter
`hot-path-imports` added and ~215 ns for a function-local import. ruff and ty
accept the syntax; ruff already offers `lazy` as the fix for `TC003`.

Three mechanisms of our own then stop being needed: the function-local
imports (272, with 53 `# noqa: PLC0415` and two per-file ignores), the
`late()` getters (17, in 8 files, plus `poop/types/_late.py`), and the
`_METHOD_BLOCK` global `block.py` installs into `_descriptor.py`. One
mechanism of the language replaces all three, and the cold paths that
`hot-path-imports` left alone get the same treatment for free.

## What Changes

- **Every function-local `from poop... import` becomes a module-level `lazy
  from ... import`**, placed after the eager imports, carrying its `#
  circular:` comment (the edge it breaks is still the reason it is lazy, and a
  `lazy` import with no cycle to break would be a smell). Names also imported
  under `if TYPE_CHECKING:` in the same module drop the typing-only copy,
  since the lazy import serves annotations too. No eager import becomes lazy:
  a class-definition-time dependency must stay eager, and the rule is
  mechanical — only what was deferred stays deferred.
- **`poop/types/_late.py` and `tests/test_late.py` are deleted**; the 17
  getters become lazy imports used as plain names. `_METHOD_BLOCK` and
  `install_method_block` go; `_descriptor.py` lazily imports `_MethodBlock`.
- **`PLC0415` becomes strict**: the two per-file ignores for `meta.py` and
  `object.py` go, and no `# noqa: PLC0415` remains anywhere.
- **The guard is widened**: `tests/test_hot_paths_bind_late.py` becomes
  `tests/test_no_local_imports.py`, keeps its hot-path operations, and adds a
  run over every example program with the import recorder on, asserting that
  no `poop/`-internal import fires from inside a function anywhere — not only
  on the hot paths.
- **Docs**: `CONTRIBUTING.md`'s Imports section is rewritten around `lazy`
  (its sentence "the function-local import is the only spelling that works
  for the cycles" is no longer true on 3.15); the `pyproject.toml` comments on
  `PLC0415` and `TC` follow; `INFECTIONS.md`'s hot-paths paragraph and the
  Object paragraph that cite `_late.py` and the installed global are updated.

No observable behavior changes: every message answers what it answered; the
refusal sentences are untouched; `skip_specs` is declared.

Out of scope, and why: the 203 imports under `if TYPE_CHECKING:` (phase 2,
if wanted — unifying on `lazy` is uniformity, not behavior or speed, and it
touches 79 files); `sys.set_lazy_imports("all")` with a filter, which would
hide the per-edge decision this codebase writes down; the handful of
function-local stdlib imports that are inside `TYPE_CHECKING` blocks already.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — source-level refactor; `skip_specs: true`)

## Impact

- `poop/types/*.py` (253 sites), `poop/transformers/*.py` (9),
  `poop/validators/*.py` (6), `poop/*.py` (4); `poop/types/_late.py`
  deleted; `poop/types/_descriptor.py`, `block.py`, `object.py`, `meta.py`.
- Tests: `tests/test_late.py` deleted; `tests/test_hot_paths_bind_late.py`
  renamed and widened; any test asserting `_late` or `_METHOD_BLOCK`.
- Docs and config: `CONTRIBUTING.md`, `pyproject.toml`, `INFECTIONS.md`.
  `README.md` counts are unchanged.
