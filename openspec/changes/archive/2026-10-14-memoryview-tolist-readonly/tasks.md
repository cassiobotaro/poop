# Tasks

## 1. MemoryView (specs/memoryview-type)

- [x] 1.1 In `poop/types/memory_view.py`, add `tolist()` answering `List(*(Int(b) for b in self._value))` (no argument; a `List` of `Int`, as `__iter__` already yields) and `readonly()` answering `to_boolean(self._value.readonly)` — a method, not a `property`, by the "numeric accessors are messages too" rule; verify `uv run poop` on `memoryview(b"ab").tolist().print()` prints `97 98` (a `List` prints its elements joined by a space) and `memoryview(b"ab").tolist().class_name().print()` prints `list`, `memoryview(b"ab").readonly().print()` prints `True` and `memoryview(bytearray(b"ab")).readonly().print()` prints `False`.
- [x] 1.2 Add tests in `tests/test_types/test_memory_view.py` for every scenario in `specs/memoryview-type/spec.md` (bytes, bytearray, slice, empty view; read-only over bytes, writable over bytearray, slice of a bytearray view; the uncalled spelling refused); verify `uv run pytest tests/test_types/test_memory_view.py -q` passes.
- [x] 1.3 In `INFECTIONS.md`: rewrite the end of the "buffer-protocol attributes stay out" paragraph under MemoryView so it no longer defers `tolist` and `readonly` but says what they answer and why `readonly` is a message (same rule as `real`/`imag`/`Range.start`), and add two rows (`tolist()`, `readonly()`) to the "Builtin-mirroring method signatures" table; verify every snippet added runs under `uv run poop` and `grep -n "left for their own change" INFECTIONS.md` finds nothing.

## 2. Integration

- [x] 2.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, and `openspec validate "memoryview-tolist-readonly" --strict`; verify every step exits 0 and coverage stays at or above 95%.
- [x] 2.2 Re-run the mechanical surface diff for `memoryview` against `MemoryView`'s MRO and verify the only names it still reports are the `INFECTIONS.md` declines (`shape`, `strides`, `suboffsets`, `itemsize`, `ndim`, `nbytes`, `c_contiguous`, `f_contiguous`, `contiguous`, `cast`, `toreadonly`, `release`, `obj`; `format` is declined too but never reported, since `Object.format` already sits on the MRO with the spec-formatting meaning).

## Workflow follow-up

- One commit for group 1 (`feat(types): MemoryView answers tolist and readonly`), code, tests and `INFECTIONS.md` together; push, check CI; archive with `/opsx:archive`, which creates `memoryview-type` as a new main spec; commit the archive.
