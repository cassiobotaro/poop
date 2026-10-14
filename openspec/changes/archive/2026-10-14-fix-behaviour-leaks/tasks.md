# Tasks

## 1. Collections and sequences

- [x] 1.1 In `poop/types/_iterable_mixin.py`, replace the `total += item` loop in `sum` with `functools.reduce(operator.add, items, total)` and add tests in `tests/test_types/test_list.py` for the three `collection-iterable-methods` scenarios (first element untouched and not identical to the answer, `start` untouched, numbers unchanged); verify `uv run pytest tests/test_types/test_list.py -q` passes.
- [x] 1.2 In `poop/types/slice.py`, refuse a `Slice` first argument accompanied by a non-absent `stop` or `step` in `_resolve_py_slice` with `#slice takes a slice or bounds, not both — write .slice(slice(1, 3)) or .slice(1, 3)`, collapse the two branches into one expression, and add tests in `tests/test_types/test_slice.py` for the four `slice-type` scenarios; verify the slice tests pass and `grep -rn "slice bounds must be int" poop/` still finds the existing refusal.
- [x] 1.3 Move `hex` onto `_BytesLikeMixin` in `poop/types/_bytes_like.py` with the `(str, bytes)` kinds, delete the copies in `bytes.py` and `byte_array.py`, make `MemoryView.hex` call the same body, trim the mixin docstring's "what differs" list, and add tests in `tests/test_types/test_byte_array.py` for the three `bytearray-type` scenarios; verify the byte tests pass and that `bytearray(b"ab").hex(1, 2, 3)` still reports `bytes.hex()` in its arity sentence (the mixin's cloak), by running the expression under `uv run poop`.

## 2. Reflection

- [x] 2.1 Change `Object.get_attr` (`poop/types/object.py`) and `PoopMeta.get_attr` (`poop/types/meta.py`) to `default: object = MISSING` from `poop/types/_sentinel.py`, branching on the marker, and add tests in `tests/test_types/test_object.py` and `tests/test_types/test_meta.py` for the three `object-type` scenarios (default answered; instance refusal `object.get_attr() takes from 2 to 3 positional arguments but 4 were given`; class refusal `get_attr() takes from 2 to 3 positional arguments but 4 were given`); verify the tests pass and `tests/test_no_python_wording.py` still passes.

## 3. Transformers

- [x] 3.1 Move the one-argument rule into `_poop_slice_from` (`poop/transformers/slice.py`), delete `_SliceRewriter.call_args` and `BuiltinRewriter.call_args` (`poop/transformers/base.py`, including its docstring mention), drop the `SliceTransformer`-after-`NoneTransformer` sentence from `poop/transformers/_registry.py`, and add tests in `tests/test_transformers/test_slice.py` for the four `slice-transformer` scenarios; verify `uv run pytest tests/test_transformers tests/test_types/test_slice.py -q` passes and `examples/` still run (`for f in examples/**/*.py; do uv run poop "$f" >/dev/null || echo "$f"; done` prints nothing).
- [x] 3.2 Delete `_DictRewriter.visit_Call`, `_merge_call` and `_pairs_call` in `poop/transformers/dict.py` (inline `call_at("_poop_dict_from_pairs", …)` in `_fold_parts` and `visit_Dict`), reduce `_FrozenDictRewriter` in `poop/transformers/frozen_dict.py` to a plain `BuiltinRewriter`, and add tests in `tests/test_transformers/test_dict.py` for the four `dict-transformer` scenarios; verify the dict and frozen_dict tests pass and `uv run poop --transformers-only` on `dict(a, x=1, **b)` shows `_poop_dict_from(a, x=_poop_int(1), **_poop_kwargs_from(b))`.
- [x] 3.3 In `poop/transformers/string.py`, leave the docstring position of a module, class and function body unwrapped (`ast.get_docstring(node, clean=False)`), and in `poop/transformers/varargs.py` insert the prologue after it; add tests in `tests/test_transformers/test_str.py` and `tests/test_transformers/test_varargs.py` for the five `str-transformer` and `varargs-transformer` scenarios; verify the transformer tests pass and `uv run poop --transformers-only` on a class with a docstring shows the docstring unwrapped.

## 4. Validators and the REPL

- [x] 4.1 Add `self.generic_visit(node)` to `_Visitor.visit_arg` in `poop/validators/no_poop_prefix.py` and tests in `tests/test_validators/test_no_poop_prefix.py` for the two `no-poop-prefix-validator` scenarios; verify they pass and `uv run poop --validators-only` on `def m(self, x: _poop_int)` reports the refusal with the caret under the annotation.
- [x] 4.2 In `poop/repl.py`, make `_displaying_through` record whether `sys.ps1`/`sys.ps2` existed and delete them on exit when they did not, and add tests in `tests/test_repl.py` for the two `repl` scenarios; verify `uv run pytest tests/test_repl.py -q` passes and `uv run python -c "import sys; from poop.repl import _displaying_through; exec('with _displaying_through(print, \">\", \".\"): pass'); print(hasattr(sys, \"ps1\"))"` prints `False`.

## 5. Docs and integration

- [x] 5.1 Update `INFECTIONS.md`: the Slice section (the fold is at runtime; the mixed form is refused), the Dict transformer section (no merge fold for calls), the `_poop_*` section (annotations are covered) and the Str transformer section (docstrings are left alone); verify every snippet added runs under `uv run poop` and `uv run pytest tests/test_doc_counts.py -q` passes.
- [x] 5.2 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate "fix-behaviour-leaks" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `fix(types): sum adds, slice refuses the mixed form, hex has one body` (1), `fix(types): get_attr takes one default` (2), `fix(transformers): slice counts at runtime, dict splats unpack like any call, docstrings stay` (3), `fix: no_poop_prefix reads annotations; the REPL puts sys.ps1 back` (4), `docs: record the four behaviors` (5); push, check CI; archive with `/opsx:archive`; commit the archive.
