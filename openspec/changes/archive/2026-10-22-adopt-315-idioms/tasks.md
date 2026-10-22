# Tasks

## 1. Comprehension unpacking (PEP 798)

- [x] 1.1 Rewrite `poop/transformers/_registry.py` — `Counter(*src for src in sources)`, `{**src for src in sources}`, `frozenset(*getattr(cls.rewriter, "names", ()) for cls in _TRANSFORMER_CLASSES)` — and drop the `chain` import; verify `uv run pytest tests/test_transformers -q` passes and `RESERVED_NAMES` and `DEFAULT_NAMESPACE` are unchanged (compare `sorted(...)` of each against a copy taken before the edit, in the scratchpad).
- [x] 1.2 Rewrite the two `list(chain.from_iterable(pairs))` in `poop/transformers/dict.py` as `[*pair for pair in pairs]` and drop `chain` from the import; verify `uv run pytest tests/test_transformers/test_dict.py -q` passes and `uv run poop --transformers-only examples/basics/hello_world.py` output is unchanged against a copy taken first.
- [x] 1.3 Rewrite the nested `for` in `poop/repl.py` (`_explain_calls`, line 267) and `poop/types/_alias.py` (`_payload_slots`, line 73) with `*`; verify `uv run pytest tests/test_repl.py tests/test_types/test_alias.py -q` passes and `uv run ruff check` reports nothing.

## 2. Markers on the sentinel builtin (PEP 661)

- [x] 2.1 Rewrite `poop/types/_sentinel.py`: five bare `NAME = sentinel("NAME")` declarations, no `_Marker`, no `Literal` aliases, no `Final`; rewrite the docstring to say why the builtin and why bare (design.md — Decisions); verify `uv run python -c "from poop.types._sentinel import MISSING; print(repr(MISSING))"` prints `MISSING`.
- [x] 2.2 Update the 22 importers: import lines drop `Missing`/`Unpeeked`/`NotACount`/`NotNumeric`/`NotIntegral`, and every annotation `| Missing` etc. becomes `| MISSING` etc. (63 + 5 sites); verify `grep -rn "Missing\b\|Unpeeked\|NotACount\|NotNumeric\|NotIntegral" poop` is empty, `uv run ty check poop/ tests/` passes, and `uv run pytest tests/test_types -q` passes.
- [x] 2.3 Correct the last sentence of the `sentinel` paragraph in `INFECTIONS.md` (line 1447: the internal `_sentinel.py` is now built on the builtin, with `|` in the interpreter's own annotations as the PEP's use); verify `grep -n "predates the builtin" INFECTIONS.md` is empty and `uv run pytest tests/test_doc_counts.py -q` passes.

## 3. prefixmatch

- [x] 3.1 Replace the seven `.match(` calls on compiled patterns in `poop/types/_message.py` (lines 115, 244, 249 ×2) and `poop/types/string.py` (lines 131, 135, 141) with `.prefixmatch(`; verify `grep -rn "\.match(" poop` is empty and `uv run pytest tests/test_types tests/test_no_python_wording.py -q` passes (the regex sites are reached through the type tests and the wording sweep; no module tests `_message.py` by name).

## 4. Integration

- [x] 4.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading pytest's summary line and gating on its exit code, and `openspec validate adopt-315-idioms --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group (`refactor(transformers)`, `refactor(types)`, `refactor(types)` for the regex); push, check CI; archive with `/opsx:archive`.
