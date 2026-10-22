# Tasks

## 1. Float predicates

- [ ] 1.1 Add `isnan`, `isinf`, `isfinite`, `isnormal`, `issubnormal` and `signbit` to `poop/types/float.py`, each `to_boolean(math.<name>(self._value))`, placed beside `is_integer`; verify `uv run pytest tests/test_types/test_float.py -q` passes with one new test per scenario in `specs/float-type/spec.md` (NaN, inf, finite and not, normal one, zero not normal, subnormal `5e-324`, `-0.0` sign bit, `0.0` not, `-2.5`), and `uv run ty check poop/ tests/` passes.
- [ ] 1.2 Rewrite the last sentence of the `math.integer` paragraph in `INFECTIONS.md` (line 1270) to say `Float` now answers the six, and add a `**`Float` answers the `math` predicates**` paragraph after the `from_number` one (line 1282) giving the reason (single receiver, CPython's spelling, `fmax`/`fmin` left out and why); verify `grep -n "deliberately untouched" INFECTIONS.md` is empty and `uv run pytest tests/test_doc_counts.py -q` passes.

## 2. Integration

- [ ] 2.1 Run `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading pytest's summary line and gating on its exit code, and `openspec validate float-answers-315-math --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit (`feat(types): Float answers the math predicates`); push, check CI; archive with `/opsx:archive`.
