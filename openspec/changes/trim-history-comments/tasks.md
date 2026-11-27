# Tasks

Each sweep task reads every file it names in full, applies design decision 1
to each passage that narrates a past state, and is one commit,
`docs(<area>): state the current reason, not the history`. "The gate" in a
task below means all of these pass:

- `uv run python openspec/changes/trim-history-comments/ast_unchanged.py`
  reports no file (task 1.3).
- `uv run pytest` exits 0 with its summary line read (95% coverage floor).
- `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/`
  exit 0.
- `git grep -niE "used to|no longer|previously" -- <the task's files>` comes
  back empty, or every remaining hit is current reasoning and is listed in
  the commit body.

## 1. Rule first

- [x] 1.1 Write the ADR with the `adr` skill: the next number in `doc/adr/`, dated 2026-11-26, status Accepted, titled for the decision (a comment states why the code is as it is; the history of a change lives in its commit and its ADR). Run the `unslop` skill on it. Verify: the file is named `NNNN-<slug>.md` with the next number, and `git grep -n "Date: 2026-11-26"` lists it.
- [x] 1.2 Add a *Comments* subsection to `CONTRIBUTING.md` under *Conventions*, between *Imports* and *Language*. It states the rule in two or three sentences and links the ADR from 1.1. Run the `unslop` skill on the new prose, and commit 1.1 and 1.2 separately. Verify: `grep -n "^### Comments" CONTRIBUTING.md` sits between the two headings, and the link resolves to the file from 1.1.
- [x] 1.3 Write `openspec/changes/trim-history-comments/ast_unchanged.py`. For every `poop/**/*.py` that differs from `main`, it parses both versions, drops each module, class and function docstring that is not the body's only statement, compares `ast.dump`, and prints each file that differs. Exit 1 if any file differs. Verify: on a scratch edit that changes a comment it prints nothing, and on a scratch edit that changes a token it prints that file. Revert both scratch edits.

## 2. Core

- [ ] 2.1 Sweep `poop/cli.py`, `poop/errors.py`, `poop/executor.py`, `poop/interpreter.py`, `poop/parser.py`, `poop/console.py` and `poop/repl.py`. Verify: the gate.

## 3. Transformers

- [ ] 3.1 Sweep every module under `poop/transformers/`. The current hits are in `slice.py`, `string.py`, `object.py`, `dict.py`, `_registry.py`, `_collection.py` and `_arity.py`, but read every file. Verify: the gate.

## 4. Validators

- [ ] 4.1 Sweep every module under `poop/validators/`. The current hits are in `no_private_attribute.py`, `no_try.py`, `no_id.py`, `no_dunder_name.py`, `no_dunder_def.py`, `no_dunder_attribute.py` and `base.py`. Verify: the gate.

## 5. Types

- [ ] 5.1 Sweep the hubs: `poop/types/object.py`, `meta.py`, `exceptions.py`, `error.py`, `mirrors.py`, `boolean.py`, `none.py`, `block.py` and `string.py`. Verify: the gate.
- [ ] 5.2 Sweep the numbers: `int.py`, `float.py`, `complex.py`, `_numeric_compare.py`, `_pow.py` and `_minmax.py`. Verify: the gate.
- [ ] 5.3 Sweep the collections and their iterators: `list.py`, `tuple.py`, `set.py`, `frozen_set.py`, `dict.py`, `frozen_dict.py`, `mapping_proxy.py`, `range.py`, `slice.py`, every `*_iterator.py`, `dict_items.py`, `dict_keys.py`, `dict_values.py`, `enumerate.py`, `zip.py`, `map.py` and `filter.py`. Verify: the gate.
- [ ] 5.4 Sweep the binary types: `bytes.py`, `byte_array.py` and `memory_view.py`. Verify: the gate.
- [ ] 5.5 Sweep `try_.py`, `with_.py`, `sentinel.py`, `ellipsis.py` and every remaining `_`-prefixed helper module under `poop/types/`. Verify: the gate, and `git ls-files 'poop/types/*.py'` lists no file that 5.1–5.5 did not name or cover.

## 6. Integration

- [ ] 6.1 Run `git grep -niE "used to|no longer|previously" -- 'poop/*.py'` across the whole package, and confirm each remaining hit is current reasoning. Run the gate once more on the final tree. Record the before and after counts of comment and docstring lines in the archive commit body. Verify: every listed hit is justified in that body.

## Workflow follow-up

- Archive with the `openspec-archive-change` skill (CONTRIBUTING.md, *Closing a change*). Then delete `ast_unchanged.py`, or keep it in the archive as the record of how the gate was run.
