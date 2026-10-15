# Tasks

## 1. Validators

- [x] 1.1 Add `ast.TypeVar`, `ast.ParamSpec` and `ast.TypeVarTuple` to `NoTypeAliasValidator` with the spelled `drop the [T]` / `[*Ts]` / `[**P]` sentence, add `tests/test_validators/test_no_type_alias.py` cases for a generic class, a generic method, a generic `type` statement and the `--validators-only` ordering; verify `uv run pytest tests/test_validators/test_no_type_alias.py -q` passes and `uv run poop --validators-only` on a `class X[T]:` file reports the sentence instead of `No validation errors.`
- [x] 1.2 Add `poop/validators/no_class_keyword.py` (an `ErrorCollector` with `visit_ClassDef` reporting each keyword, `**name` for a splat), register it after `NoDecoratorValidator`, add its test module and a `class X(foo=1)` snippet to `_EXPLAIN_SNIPPETS` in `poop/repl.py`; verify its tests and `tests/test_repl.py` pass and `:explain class_keyword` (or the topic name chosen) answers the sentence.
- [x] 1.3 Add `poop/validators/no_dunder_def.py` with the deny-list rows and per-row sentences from the spec, register it after `no_class_keyword`, add a test parametrised over `dir(object)` (each dunder is refused, documented-legal, or not definable), and an `_EXPLAIN_SNIPPETS` entry; verify `uv run pytest tests/test_validators/test_no_dunder_def.py tests/test_repl.py -q` passes and every program under `examples/` still validates (`for f in examples/*/*.py; do uv run poop --validators-only "$f"; done`).
- [x] 1.4 Extend `no_class_machinery`'s visitor with a function-kind stack so `super()` under a `lambda` and `return <value>` directly in `__init__` are refused with the spec's sentences; verify `uv run pytest tests/test_validators/test_no_class_machinery.py -q` passes with new cases for both, and that `examples/patterns/template_method.py` (which uses `super()` in a method) still runs.
- [x] 1.5 Update `README.md` (validator count 73 and the "Syntax shortcuts" / "Introspection" bullets), `INFECTIONS.md` (sections for `no_class_keyword` and `no_dunder_def`, a paragraph under `no_type_alias` and `no_class_machinery`) and `MIGRATION.md` (rows for `class X[T]`, `class X(metaclass=…)`, `__getattr__`); verify `uv run pytest tests/test_doc_counts.py -q` passes and each new doc snippet runs through `uv run poop --validators-only`.

## 2. Runtime surfaces

- [x] 2.1 Hand `Str(name)` to `does_not_understand` in `Object.__getattribute__` and read it back as `str(name)` in the three built-in hooks (`Object`, `Error`, `PoopMeta`); add a `tests/test_types/test_object.py` case where a user hook returns the name and the program sends `.upper()` to it; verify `uv run pytest tests/test_types/test_object.py tests/test_types/test_error.py tests/test_no_python_wording.py -q` passes.
- [x] 2.2 Bind `_poop_slice_cls = builtin_alias(Slice, _poop_slice_from, "slice")` in `poop/transformers/slice.py` and point `name_target` at it; add `tests/test_transformers/test_slice.py` cases for `s = slice; s(5)`, `class S(slice)` and the four-argument refusal through the alias; verify `uv run pytest tests/test_transformers/test_slice.py tests/test_types/test_slice.py tests/test_transformers/test_namespace.py -q` passes.
- [x] 2.3 Give the root mirror an instance side in `exceptions._build` (`message`, `kind`, `raise_`, `__str__` in the `Error` shape) and refuse `args`, `add_note`, `with_traceback` on instances through `_refuse_python_attribute`; add `tests/test_types/test_exceptions.py` cases for each spec scenario, including a `class Field(Exception)` with a field; verify `uv run pytest tests/test_types/test_exceptions.py tests/test_types/test_try.py tests/test_no_python_wording.py -q` passes and `uv run poop examples/idiomatic/managed_resource.py` runs.
- [x] 2.4 Document the exception instance side in `INFECTIONS.md` (under `PoopExcMeta`) and the slice alias under `Slice`; verify the snippets run with `uv run poop`.

## 3. Integration

- [x] 3.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate close-raw-python-leaks --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per task (one validator, one surface each), in dependency order; push, check CI.
- Archive with `/opsx:archive` (delta specs sync into `openspec/specs/`); commit the archive.
