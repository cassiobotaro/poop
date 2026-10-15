# Tasks

## 1. Transformers

- [ ] 1.1 Declare `names = frozenset(MIRRORS)` on `_ExceptionRewriter`, read it in `visit_Name`, and drop the union and comment in `no_builtin_shadow.py`; verify `uv run pytest tests/test_transformers/test_exception.py tests/test_validators/test_no_builtin_shadow.py -q` passes and `RESERVED_NAMES` still contains `ValueError` (assert it in the namespace test).
- [ ] 1.2 Add `LiteralRewriter` to `_collection.py`, reduce `list.py`, `tuple.py`, `set.py` to attribute declarations, derive `_LITERAL_KIND` from them; verify `uv run pytest tests/test_transformers -q` passes and `uv run poop --transformers-only examples/idiomatic/pipeline.py` unparses as before (diff against a copy taken first).

## 2. Types

- [ ] 2.1 Delete `List.sorted`, `Str.min`/`max`, `_MappingMixin.min`/`max`; rewrite the `_minmax.py` paragraph and drop the `INFECTIONS.md` sentence keeping `List`'s override; verify `uv run pytest tests/test_types/test_list.py tests/test_types/test_string.py tests/test_types/test_dict.py tests/test_no_python_wording.py -q` passes and `[3, 1].sorted().class_name().print()` prints `list`.
- [ ] 2.2 Delete `Boolean.__repr__`; read `_slots` inside `_endow` and drop its parameter and `noqa`; align `With`'s single-use mechanism with `Try`'s (`del` plus a flag); drop the default `role=` on the four `a_block` calls in `boolean.py`; verify `uv run pytest tests/test_types/test_boolean.py tests/test_types/test_alias.py tests/test_types/test_try.py tests/test_types/test_with.py -q` passes.
- [ ] 2.3 Share `fromhex` through a `_from_hex(cls, native, s)` helper in `_bytes_like.py`, delete the orphaned comment in `ByteArray.iter`, widen the `max`/`min` annotations on `Int` and `Boolean` to `Int | Float | Boolean` and the `index` bounds in `_sequence.py`, `list.py`, `tuple.py` to `Index`; verify `uv run ty check poop/ tests/` and `uv run pytest tests/test_types/test_bytes.py tests/test_types/test_byte_array.py tests/test_types/test_int.py -q` pass.

## 3. Validators

- [ ] 3.1 Reword to `Klass` in `no_issubclass.py`, add `()` to `no_print.py`'s sentence, unify the no-substitute sentence in `no_breakpoint.py`, `no_exit.py`, `no_help.py`, `no_open.py`, fix `dunder_message`'s label for a class-body `__slots__`, and generate `no_comprehension.messages` from one tail; update each validator's test, `INFECTIONS.md`, `README.md` and `tests/test_repl.py`'s `:explain` expectations; verify `uv run pytest tests/test_validators tests/test_repl.py tests/test_doc_counts.py -q` passes and `grep -rn "Class.is_subclass\|^print is forbidden\|no POOP equivalent" poop tests *.md` is empty.

## 4. Tests

- [ ] 4.1 Move `EXAMPLES_DIR`/`EXAMPLE_FILES` into `tests/_support.py`, use them from the four discovering modules, and add `tests/test_examples_docstring.py` parametrised over every example asserting its docstring starts with a `Smalltalk` header; verify `uv run pytest tests/test_examples_docstring.py tests/test_pipeline.py tests/test_doc_counts.py -q` passes with 44 docstring cases.
- [ ] 4.2 Split `tests/test_no_local_imports.py`'s monolith into a module-scoped warm-up fixture and one parametrised recorded pass per example; verify `uv run pytest tests/test_no_local_imports.py -q --durations=3` shows per-example cases and the module's total time is within 10% of before.
- [ ] 4.3 Use the `repl` fixture for every bare `Repl(Interpreter())` in `tests/test_repl.py`, parametrise the `_indent_for` and `_value_text` tables, and parametrise `tests/test_cli.py`'s three clean-diagnostic cases; verify `uv run pytest tests/test_repl.py tests/test_cli.py -q` passes with the same number of assertions (count cases before and after).

## 5. Integration

- [ ] 5.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate dedupe-types-and-validators --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group (`refactor(transformers)`, `refactor(types)`, `refactor(validators)`, `test:`); push, check CI.
- Archive with `/opsx:archive` (no delta specs); commit the archive.
