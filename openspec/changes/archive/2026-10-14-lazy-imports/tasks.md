# Tasks

## 1. The hub, as the pilot

- [x] 1.1 Lift the function-local `poop` imports of `poop/types/_descriptor.py`, `object.py`, `meta.py` and `block.py` to module-level `lazy from` imports (keeping each `# circular:` comment, dropping each `# noqa: PLC0415`, removing a `TYPE_CHECKING` copy of a name now imported lazily), replace `_METHOD_BLOCK`/`install_method_block`/`_method_block` in `_descriptor.py` with `lazy from poop.types.block import _MethodBlock` used as a plain name, and remove the install line from `block.py`; verify `uv run ruff check && uv run ty check poop/ tests/ && uv run pytest -q` passes (reading the `N passed` line) with coverage still reported, before touching any other file.

## 2. The rest of the tree

- [x] 2.1 Write a one-off script in the scratchpad that, for every module under `poop/`, finds each `ImportFrom` of a `poop` module whose enclosing scope is a function, lifts it to a deduplicated `lazy from` block after the last eager import (first `# circular:` comment carried), deletes the function-local lines and their `# noqa: PLC0415`, and drops a `TYPE_CHECKING` import of the same name; run it over `poop/types/*.py` (the remaining ~240 sites), then `uv run ruff check --fix && uv run ruff format`; verify `grep -rn "^\s\+from poop\." poop/types/ | grep -v "^[^:]*:[0-9]*:    from" ` finds nothing, that no eager import was moved (`git diff` shows only removed indented imports and added `lazy from` lines in import blocks), and `uv run pytest tests/test_types -q` passes.
- [x] 2.2 Run the same lift over `poop/transformers/*.py`, `poop/validators/*.py` and `poop/*.py` (19 sites), replace the 17 `= late(...)` getters and their `_x()` call sites in `int.py`, `meta.py`, `_numeric_compare.py`, `object.py`, `_argument.py`, `boolean.py`, `_iterable_mixin.py` with the lazily imported names, delete `poop/types/_late.py` and `tests/test_late.py`; verify `grep -rn "late(\|_late" poop/ tests/` finds nothing and the full suite passes.

## 3. Lint, guard and measurement

- [x] 3.1 In `pyproject.toml`, remove the `PLC0415` per-file ignores for `meta.py` and `object.py`, and rewrite the two comments on `PLC0415` and `TC` to state the new rule (a cycle is broken by a module-level `lazy from`; a function-local import is never written; annotation-only imports stay under `TYPE_CHECKING`); verify `uv run ruff check` passes with no `noqa: PLC0415` left (`grep -rn "PLC0415" poop/` finds nothing).
- [x] 3.2 Rename `tests/test_hot_paths_bind_late.py` to `tests/test_no_local_imports.py`, update its docstring, and add `test_no_example_fires_a_local_import`: run every `examples/**/*.py` that does not read `input` through `Interpreter().run_source` with stdout captured and the recorder armed, asserting the record is empty; verify it passes, and that re-adding one function-local `from poop.types.tuple import Tuple` to a hot method makes it fail naming the site.
- [x] 3.3 Run the twelve-operation micro-timing script against `main` before 1.1 and the tree after 2.2, same session, record both columns under `## Measured` in `design.md`; verify no operation is slower by more than 5 % and stop to report if one is.

## 4. Docs

- [x] 4.1 Rewrite the Imports section of `CONTRIBUTING.md`: imports live at the top; a cycle is broken by `lazy from ... import ...` at the top with a `# circular:` comment naming the edge, never by a function-local import; annotation-only imports stay under `if TYPE_CHECKING:`; keep the explanation of why the hubs cannot import eagerly; verify the section no longer says the function-local import is the only spelling that works.
- [x] 4.2 In `INFECTIONS.md`, update the hot-paths paragraph (it names `_late.py`, `late()`, the installed global and the "rule for the next site") and the Object paragraph's mention of `block.py` installing the class, so both describe `lazy from` as the mechanism and record the 30 ns / 70 ns / 215 ns measurement; verify every snippet runs under `uv run poop` and `grep -c "_late" INFECTIONS.md` is 0.

## 5. Integration

- [x] 5.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate "lazy-imports" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `refactor(types): the hub imports lazily` (1), `refactor: every deferred import is a lazy import` (2, with the `pyproject` change of 3.1 since the hooks lint staged files), `test: no local import fires anywhere; record the measurement` (3), `docs: lazy imports are the spelling for a cycle` (4); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
