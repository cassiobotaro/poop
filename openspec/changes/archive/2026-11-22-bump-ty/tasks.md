# Tasks

## 1. Class-side raise_ keeps no keyword for itself

- [x] 1.1 Add two tests to `tests/test_types/test_exceptions.py`, next to `test_raise_carries_keyword_arguments`: `class Tagged(Exception)` storing `self.cls = cls`, raised with `Tagged.raise_(cls="x")`, whose handler prints `e.cls` and the output is `x`; and `class Plain(Object)` sent `Plain.raise_(cls="x")`, whose handler prints `e.message()` and the output is `Plain cannot be raised — only a class descending from Exception can`. Verify both fail before the fix with `got multiple values for argument 'cls'` in the failure (`uv run pytest tests/test_types/test_exceptions.py -q --no-cov`).
- [x] 1.2 Make the receiver positional-only in both signatures: `def raise_(cls, /, *args: object, **kwargs: object) -> Never` in `poop/types/exceptions.py` (`PoopExcMeta`) and `poop/types/meta.py` (`PoopMeta`, under `@class_side_refusal`), keeping each `noqa` and its reason; verify the two tests of 1.1 pass and `uv run pytest tests/test_types -q --no-cov` exits 0.
- [x] 1.3 Add to the `raise_` paragraph of `INFECTIONS.md` (the one ending "…must be raisable", near line 1471) that the receiver is taken positionally so no keyword is kept from the program, with `Tagged.raise_(cls="x")` and the sentence it used to answer; run the snippet through `uv run poop` from a scratchpad file and verify it prints `x`, and that `uv run pytest tests/test_doc_counts.py -q --no-cov` exits 0.

## 2. sum binds its result gradually

- [x] 2.1 In `_IterableMixin.sum` (`poop/types/_iterable_mixin.py`), bind the fold to `result: Any = functools_reduce(operator.add, items, total)` and return `result`, extending the comment above `total` to say the answer is bound the same way and why (the return annotation would otherwise drive `reduce` against `Object`); verify `uv run ty check poop/ tests/` passes under the locked 0.0.87, `uvx ty@0.0.107 check poop/types/_iterable_mixin.py` reports no error for the file, `uv run ruff check` reports nothing, and `uv run pytest tests/test_types -q --no-cov -k sum` exits 0.

## 3. The superclass test narrows before it sends

- [x] 3.1 In `test_a_class_answers_its_superclass_as_a_class_not_a_name` (`tests/test_types/test_meta.py`), hold `_Dog.superclass()` in `superclass`, assert `superclass is _Animal`, then assert `superclass.name() == Str("_Animal")`; verify `uvx ty@0.0.107 check tests/test_types/test_meta.py` no longer reports `missing-union-attribute` and `uv run pytest tests/test_types/test_meta.py -q --no-cov` exits 0.

## 4. Bump ty and follow the renamed rules

- [x] 4.1 Raise the floor to `"ty>=0.0.107"` in `pyproject.toml` and run `uv lock --upgrade-package ty==0.0.107 && uv sync --dev`; verify `uv run ty --version` prints `0.0.107` and `git diff --stat uv.lock` touches only the `ty` entry.
- [x] 4.2 Rename the rules in `pyproject.toml`: `invalid-method-override` → `incompatible-method-override` under `[tool.ty.rules]`, `unresolved-attribute` → `missing-attribute` under the `tests/**` override; verify `uv run ty check poop/ tests/` reports no `renamed-rule` warning.
- [x] 4.3 Rename the rules in the ignore comments: `invalid-mutable-override` → `incompatible-mutable-override` (`poop/errors.py`, two), `invalid-return-type` → `invalid-explicit-return` (`tests/test_types/test_block.py`), `call-non-callable` → `not-callable` (`tests/test_types/test_block.py`, `tests/test_types/test_meta.py`), and `type: ignore[unresolved-attribute]` → `type: ignore[missing-attribute]` (`tests/test_message_descriptors.py`, `tests/test_types/test_object.py`); verify `uv run ty check poop/ tests/` answers `All checks passed!`.
- [x] 4.4 Rename `invalid-method-override` in `.github/copilot-instructions.md` (the "`ty` type-checking suppression" paragraph); verify `grep -rnE "invalid-method-override|unresolved-attribute|invalid-mutable-override|invalid-return-type|call-non-callable" poop tests pyproject.toml .github README.md CONTRIBUTING.md AGENTS.md INFECTIONS.md` is empty.

## 5. Integration

- [x] 5.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading pytest's summary line and gating on its exit code, and `openspec validate bump-ty --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit per group, in order: `fix(types)` for group 1 (code, tests and `INFECTIONS.md` together), `refactor(types)` for group 2, `test(meta)` for group 3, `chore(deps)` for group 4. Groups 1–3 pass the hook under the locked 0.0.87; group 4 is the commit that changes the lock.
- Push the branch, check CI on both `3.15` and `3.15t`, then archive with `/openspec-archive-change` and commit `chore(openspec): archive bump-ty`.
- Dependabot PR #86 (`ty` 0.0.101) is superseded once this is on `main`.
