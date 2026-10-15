# Tasks

## 1. Equality and errors

- [ ] 1.1 Make `_ValueEqMixin._eq_comparable` symmetric across a subclass, add `class Stack(list)` and `class Name(str)` cases (both operand orders, dict lookup) to `tests/test_types/test_value_eq.py`; verify `uv run pytest tests/test_types/test_value_eq.py tests/test_types/test_dict.py -q` passes.
- [ ] 1.2 Forward public instance state through `Error.does_not_understand`, `has_attr`, `get_attr` and `dir`, and make two `Error`s over one exception equal and hash alike; add `tests/test_types/test_error.py` cases for the spec's four scenarios; verify `uv run pytest tests/test_types/test_error.py tests/test_types/test_try.py -q` passes.
- [ ] 1.3 Give `Try` and `With` a `*args` constructor that words `got nothing` / `got N arguments`, add cases to `tests/test_types/test_try.py` and `tests/test_types/test_with.py`, and add `Try()`/`With()` to the wording sweep's constructor samples; verify `uv run pytest tests/test_types/test_try.py tests/test_types/test_with.py tests/test_no_python_wording.py -q` passes.

## 2. Collections and numbers

- [ ] 2.1 Add `Range.__len__` and `__contains__`, keep `includes` folding a `Boolean`; add truthiness, `assert_` and membership cases to `tests/test_types/test_range.py`; verify `uv run pytest tests/test_types/test_range.py -q` passes.
- [ ] 2.2 Override `class_` on `Boolean` to answer the one `bool` class and add `a_boolean` to `_argument.py` for `xor`/`eqv`; add cases to `tests/test_types/test_boolean.py`; verify `uv run pytest tests/test_types/test_boolean.py tests/test_types/test_meta.py -q` passes.
- [ ] 2.3 Swap `_faithful` for `_searched` in `MemoryView.includes/count/index`, guard `ByteArray.at_put`'s byte with `an_int` before `indexing`, and route `index`/`rindex` misses in `string.py` and `_bytes_like.py` through `no_element_equal_to`; add cases to the three type test modules; verify `uv run pytest tests/test_types/test_memory_view.py tests/test_types/test_byte_array.py tests/test_types/test_bytes.py tests/test_types/test_string.py -q` passes.
- [ ] 2.4 Guard `_poop_range`'s arguments with `an_int` (roles `start`/`stop`/`step`), rewrite the transformer docstring that kept CPython's sentence, and update `tests/test_transformers/test_range.py:80,89`; verify `uv run pytest tests/test_transformers/test_range.py tests/test_types/test_range.py -q` passes.
- [ ] 2.5 Admit a `Boolean` modulus in `Int.__pow__`, word `FrozenDict.hash` with the value's kind, and resolve `Slice.indices` bounds through the check `_resolve_py_slice` uses; add cases to `tests/test_types/test_int.py`, `test_frozen_dict.py`, `test_slice.py`; verify `uv run pytest tests/test_types/test_int.py tests/test_types/test_frozen_dict.py tests/test_types/test_slice.py -q` passes.

## 3. Class side and print

- [ ] 3.1 Add `class_side.__delete__`, wrap `PoopMeta.del_attr`'s `delattr`, and route `PoopMeta.format` and `print` through `text_like`/`_template_refusal`; add cases to `tests/test_types/test_meta.py` and the class receivers (`A.format`, `A.del_attr`) to the wording sweep; verify `uv run pytest tests/test_types/test_meta.py tests/test_no_python_wording.py -q` passes.
- [ ] 3.2 Check `end`/`sep` in `Object.print` and `_print_items` through an optional-text helper, and make the wording sweep redirect stdout for `print` instead of listing it in `_UNSENDABLE`; verify `uv run pytest tests/test_types/test_object.py tests/test_types/test_list.py tests/test_no_python_wording.py -q` passes.

## 4. Validator wording and docs

- [ ] 4.1 Reword `private_message` in `poop/validators/no_private_attribute.py` and its module docstring, update `tests/test_validators/test_no_private_attribute.py:39` and the `INFECTIONS.md` / `MIGRATION.md` lines that quote the old sentence; verify `uv run pytest tests/test_validators/test_no_private_attribute.py tests/test_doc_counts.py -q` passes and `grep -rn "get_attr(name) to ask" poop tests *.md` is empty.
- [ ] 4.2 Add an `INFECTIONS.md` paragraph per decision in `design.md` (value equality, error state, range truthiness, bool class, class-side wording, Try/With arity, the seven data-type sentences) and a note on `Sentinel` subclassability; verify each snippet runs with `uv run poop`.

## 5. Integration

- [ ] 5.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, run every example (`for f in examples/*/*.py; do uv run poop "$f" </dev/null; done`), and `openspec validate fix-wrapper-equality-and-errors --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit per task; push, check CI.
- Archive with `/opsx:archive`; commit the archive.
