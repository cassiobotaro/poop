# Tasks

## 1. The paired null test

- [ ] 1.1 Add `if_none_if_not_none` and `if_not_none_if_none` to `Object`, `NoneClass` and `PoopMeta`, checking both blocks on every receiver; add `ifNilIfNotNil` to `SMALLTALK_SELECTORS`; add cases to `tests/test_types/test_object.py`, `test_none.py`, `test_meta.py` for each spec scenario; verify `uv run pytest tests/test_types/test_object.py tests/test_types/test_none.py tests/test_types/test_meta.py tests/test_no_python_wording.py -q` passes.
- [ ] 1.2 Document the pair in `INFECTIONS.md` (`NoneClass`) and `MIGRATION.md` (`x if x is not None else d` row), and use it in `examples/idiomatic/safe_config.py` where the chained form is written today; verify `uv run poop examples/idiomatic/safe_config.py` prints what it printed and `uv run pytest tests/test_doc_counts.py -q` passes.

## 2. find with a default

- [ ] 2.1 Add the keyword-only `default` to `_IterableMixin.find` with `next`'s overload pair and the positional-refusal sentence; add cases to the iterable-mixin test module for the four spec scenarios; verify `uv run pytest tests/test_types -q -k find` passes and `uv run ty check poop/ tests/` is clean.
- [ ] 2.2 Document it in `INFECTIONS.md` (`Collection iterable methods`) and `MIGRATION.md` (`next((x for x in xs if p(x)), d)` row); verify the snippets run with `uv run poop`.

## 3. Hints

- [ ] 3.1 Extend `SMALLTALK_SELECTORS` with the proposal's rows, let a row carry a spelling, and teach `explain` the two kinds; add cases to `tests/test_types/test_selectors.py` for `first`, `isEmpty`, `timesRepeat`, `atIfAbsent` and one message-kind row; verify `uv run pytest tests/test_types/test_selectors.py -q` passes and `[1].first()` under `uv run poop` prints the spec's sentence.
- [ ] 3.2 Add the lazy-view rows to `CROSS_LANGUAGE_HINTS` for `map`, `filter`, `zip`, `enumerate` × `len`, `at`, `reversed`, `includes`, `sorted`; add cases; verify `uv run pytest tests/test_types/test_selectors.py tests/test_types/test_map.py -q` passes and the `INFECTIONS.md` hints paragraph lists the new families.

## 4. Integration

- [ ] 4.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate collection-protocol-gaps --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit per task; push, check CI.
- Archive with `/opsx:archive`; commit the archive.
