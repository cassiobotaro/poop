# Tasks

## 1. The helper and the numeric tower

- [x] 1.1 Add `poop/types/_late.py` with `late(module: str, name: str) -> Callable[[], object]` returning a `functools.cache`d zero-argument getter over `importlib.import_module(module)` and `getattr`, with a module docstring stating the rule (a cycle is broken by a local import; a hot site binds late) and the numbers (~215 ns import, ~50 ns cached getter, ~20 ns global); add `tests/test_late.py` asserting the getter resolves a name, answers the same object twice, and resolves a module not yet imported when built; verify `uv run pytest tests/test_late.py -q` passes.
- [x] 1.2 In `poop/types/_numeric_compare.py`, rewrite `_num_value` as `isinstance(other, _NumericCompareMixin)` then `other._order_value()` else `NOT_NUMERIC` (no imports), bind `to_boolean` and `false` through `late`, and reorder `__eq__` to coerce first and ask for `Complex` (late-bound) only on `NOT_NUMERIC`; update the module docstring's description of `_num_value`; verify `uv run pytest tests/test_types/test_int.py tests/test_types/test_float.py tests/test_types/test_boolean.py tests/test_types/test_complex.py tests/test_no_python_wording.py -q` passes.
- [x] 1.3 In `poop/types/int.py`, bind `Float` and `to_poop` through `late` in `_arith` and `__pow__`; in `poop/types/boolean.py`, bind `Int` in `_as_int`; keep every other local import in both files; verify the four numeric test files pass.

## 2. Dispatch, printing and guards

- [x] 2.1 In `poop/types/object.py`, bind `_MethodBlock` through `late` in `__getattribute__` (the getter call is the only change on that path), and `Str`, `none`, `_unwrap`/`_unwrap_bool` in `print`, `repr` and `ascii`; in `poop/types/meta.py`, bind `unalias` and `to_boolean` in `__eq__`/`__ne__`; verify `uv run pytest tests/test_types/test_object.py tests/test_types/test_meta.py tests/test_types/test_block.py -q` passes.
- [x] 2.2 In `poop/types/_argument.py`, bind `_is_absent` and `_searched` through `late` at the six guard sites; in `poop/types/_iterable_mixin.py`, bind `Map` and `Filter` in `map` and `filter`; verify `uv run pytest tests/test_types/test_argument.py tests/test_types/test_map.py tests/test_types/test_filter.py -q` passes.

## 3. The guard and the measurement

- [x] 3.1 Add `tests/test_hot_paths_bind_late.py`: patch `builtins.__import__` to record `(file, line, function)` of every import whose caller is a non-module frame under `poop/`, warm the operations once, then run `Int < Int`, `Int == Int`, `Int + Int`, `Int * Float`, `Int == Complex`, `an_int(Int)`, `(5).abs()`, `xs.at(0)`, `xs.map(block)`, `"ab".len()`, `true.if_true(block)`, `obj.print()` (stdout captured) and `int == int`, and assert the record is empty, naming any site it is not; verify the test passes, and that re-adding one local import to `_num_value` makes it fail naming `_numeric_compare.py`.
- [x] 3.2 Run the micro-timing script (the same nine operations as design.md's baseline, best of five, 20 000 iterations) against the tree before 1.1 (`git stash` or a worktree at `main`) and after 2.2, in one session, and record both columns and the ratio under `## Measured` in `design.md`; verify `Int < Int` and `Int == Int` improve by at least 20 % and `(5).abs()` by at least 10 %, and stop to report if they do not.
- [x] 3.3 In `INFECTIONS.md`, add one paragraph under the PoopMeta or Object section: the 277 local imports exist for the cycles, the counter ranked them, the measured hot sites bind late through `_late.late`, and the rule for the next contributor (local import for a cold site, `late` for one the counter test covers); verify every snippet in it runs under `uv run poop` and `grep -c "_late" INFECTIONS.md` is at least 1.

## 4. Integration

- [x] 4.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, and `openspec validate "hot-path-imports" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `perf(types): the numeric tower binds late` (1), `perf(types): message dispatch, printing and guards bind late` (2), `test: hot paths fire no local import; record the measurement` (3), each with its slice of `INFECTIONS.md` where it applies; push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
