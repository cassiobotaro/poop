# Tasks

## 1. Bindings

- [x] 1.1 Remove `_poop_boolean`, `_poop_bytearray`, `_poop_memoryview`, `_poop_frozenset`, `_poop_frozendict`, `_poop_sentinel` and `_poop_dict` (`_poop_complex` stays as the literal target of 1.2) from their transformers' `BINDINGS`, and add a test to `tests/test_transformers/test_namespace.py` that every `_poop_*` key of `DEFAULT_NAMESPACE` is emitted by some rewriter (collect every `call_target`, `name_target`, `literal_target` and the `_poop_*` names the custom rewriters emit, by running the pipeline over a corpus of literals and calls) or is a helper another binding calls; verify `uv run pytest tests/test_transformers -q` and `uv run pytest tests/test_repl.py -q` pass.
- [x] 1.2 Delete `make_constructor` from `poop/transformers/_collection.py` and bind `List`, `Tuple` and `Set` directly in `list.py`, `tuple.py`, `set.py`; delete `_poop_complex_literal` and point `literal_target` at `_poop_complex_cls`'s class binding in `complex.py`, updating `tests/test_types/test_complex.py`; delete the `Range` branch of `make_iterable_from`; verify `uv run pytest tests/test_transformers tests/test_types/test_complex.py tests/test_types/test_list.py -q` passes and `uv run poop examples/basics/hello_world.py` runs.

## 2. Shared helpers

- [x] 2.1 Add `rebind(target, helper)` to `poop/transformers/base.py`, use it from `varargs.py` and `unpack.py`, narrow `unpack.py`'s target guard to `ast.Name | ast.Attribute`, and drop the dead `if node.body` guard in `return_.py`; verify `uv run pytest tests/test_transformers/test_varargs.py tests/test_transformers/test_unpack.py tests/test_transformers/test_return_.py -q` passes.
- [x] 2.2 Normalise `range.py`'s arguments once and build one `Range`, keeping the zero-step refusal; verify `uv run pytest tests/test_transformers/test_range.py tests/test_types/test_range.py -q` passes and `range(5)`, `range(2, 5)`, `range(5, 2, -1)` and `range(1, 2, 0)` answer what they answered (compare `uv run poop` output before and after on a scratch file).
- [x] 2.3 Rewrite `_is_super_call` (`no_dunder_attribute.py`), `BuiltinRewriter.visit_Call` (`base.py`) and `_DictRewriter`'s builtin test (`dict.py`) as `match` class patterns, and spell the refused type with `__qualname__` in `int.py`, `float.py` and `sentinel.py`; verify `uv run pytest tests/test_transformers tests/test_validators/test_no_dunder_attribute.py tests/test_no_python_wording.py -q` passes.

## 3. Validators

- [x] 3.1 Add `poop/validators/_shadow.py` with `ShadowValidator(CollectingValidator)` (`protected: ClassVar[frozenset[str]]`, `message: ClassVar[str]`, one `_Visitor`), reduce `no_builtin_shadow.py` and `no_namespace_shadow.py` to subclasses, and document the fourth helper in `CONTRIBUTING.md`'s validator section; verify `uv run pytest tests/test_validators/test_no_builtin_shadow.py tests/test_validators/test_no_namespace_shadow.py -q` passes and the two refusal sentences are unchanged (grep them in the tests).

## 4. Integration

- [x] 4.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate "trim-transformers-validators" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `refactor(transformers): only emitted bindings; classes bind themselves` (1), `refactor(transformers): one rebind, one range build, patterns where they read` (2), `refactor(validators): a shared shadow validator` (3); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
