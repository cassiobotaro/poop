# Tasks

## 1. The overloads and the cast

- [x] 1.1 In `poop/types/_bridge.py`, change the container overloads to `list[Any]`, `tuple[Any, ...]`, `dict[Any, Any]`, `frozendict[Any, Any]`, `set[Any]`, `frozenset[Any]` (importing `Any`), and add one paragraph to the module docstring: the parameters are `Any` because `dict`, `list`, `set` and `frozendict` are invariant, so `object` matched no typed container and sent every one to the `object -> object` overload; the classes stay concrete because the dispatcher converts exactly those; verify `uv run ty check poop/ tests/` passes.
- [x] 1.2 In `poop/types/string.py`, `Str.maketrans`: return `to_poop(table)` directly, removing the `cast("Dict", ...)` and the three-line comment above it; verify `uv run ty check poop/` passes and `uv run pytest tests/test_types/test_str.py -q` passes.

## 2. The guard

- [x] 2.1 Add `tests/test_bridge_types.py`: a module docstring saying it is checked by ty and a no-op under pytest; one `test_` function that declares typed values with annotations (`d: dict[int, int] = {1: 2}`, `xs: list[int] = [1]`, `t: tuple[int, int] = (1, 2)`, `s: set[str] = {"a"}`, `fs: frozenset[str] = frozenset({"a"})`, `fd: frozendict[str, int] = frozendict(a=1)`) and calls `assert_type` on `to_poop(...)` of each against `Dict`, `List`, `Tuple`, `Set`, `FrozenSet`, `FrozenDict`, plus `assert_type(to_poop(str.maketrans("a", "b")), Dict)`; a comment states why literals passed straight to `to_poop` would not catch the regression (bidirectional inference matches them against the parameter); verify `uv run ty check tests/` passes, `uv run pytest tests/test_bridge_types.py -q` passes, and that reverting one overload to `dict[object, object]` makes ty report `type-assertion-failure` on the `Dict` line.

## 3. Integration

- [x] 3.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, and `openspec validate "to-poop-container-overloads" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit (`types: to_poop's container overloads are reachable`); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
