# Tasks

## 1. Prose

- [x] 1.1 Move each orphaned comment back to the method it describes in `boolean.py`, `string.py`, `byte_array.py`, `_minmax.py`, `_set_algebra.py`, `_dict_view.py` and `_mapping.py`, deleting the "bound late" / "function-local" sentences; verify by reading `git diff` that every moved comment now sits directly above a `def` or the statement it names, and `uv run ruff check` passes.
- [x] 1.2 Rewrite the four guard comments in `_bytes_like.py` (two), `memory_view.py` and `range.py` (`includes`, found while applying) to describe `a_needle`/`bytes_like`/`_faithful`/`_searched`, and the four `__ne__` sentences to say it lives on `Object`; verify `grep -n "getattr-unwrap\|__ne__" poop/types/_bytes_like.py poop/types/memory_view.py poop/types/_numeric_compare.py poop/types/int.py poop/types/float.py poop/types/boolean.py` shows only the corrected sentences.

## 2. Dead code

- [x] 2.1 Delete the `Boolean` fold in `_repeat.py` (and its import), the `Complex` pre-check in `int.py` and `float.py` (moving `Complex` under `TYPE_CHECKING` in both, where it is annotation-only), inline `Range._iter` into `__iter__` (its seven callers in `tests/test_transformers/test_range.py` iterate the `Range` directly), drop the two `# type: ignore[assignment]` on `__hash__ = None`, and delete the `_complex`/`_bytearray`/`_memoryview` aliases using the builtins directly; verify `uv run pytest tests/test_types/test_repeat.py tests/test_types/test_int.py tests/test_types/test_float.py tests/test_types/test_range.py tests/test_types/test_complex.py tests/test_types/test_byte_array.py tests/test_types/test_memory_view.py -q` passes (`tests/test_types/test_repeat.py` may not exist: then run `test_list.py` and `test_str.py`, which cover `*`) and `uv run ty check poop/ tests/` passes.

## 3. Spellings

- [x] 3.1 In `_iterable_mixin.py`, move the runtime imports above the `TYPE_CHECKING` block and replace `@abstractmethod` on `__iter__` with `raise NotImplementedError`; in `boolean.py`, import `MISSING` from `_sentinel` and drop the `bool()` in `from_bytes`; type `_codec._refusal` as `UnicodeEncodeError | UnicodeDecodeError` reading `.start`/`.object` directly; normalise `Float.__init__` with `float(...)` (`hex` keeps its `float(...)` for the checker alone: a `float` annotation admits `int`, which has no `hex`), adding a test that `Float(1)` prints `1.0`; verify `uv run pytest tests/test_types -q` passes.
- [x] 3.2 Rename the enum in `_sentinel.py` to `_Marker` (members and the `Missing` alias unchanged) and update its importers; verify `grep -rn "from poop.types._sentinel import" poop tests` shows no `Sentinel` and the suite passes.
- [x] 3.3 In `poop/transformers/_registry.py` drop the `_`-aliases on the stdlib imports; in `poop/cli.py` split `_read_source`'s handler into `except OSError` and `except UnicodeDecodeError` sharing one `_write`/`raise` through a small helper; in `poop/repl.py` write `_value_text` as a `match`; in `meta.py` and `exceptions.py` wrap the installing loops in a function called once; in `_message.withheld_builtin` test `name in vars(builtins)`; verify `uv run pytest tests/test_cli.py tests/test_repl.py tests/test_types/test_meta.py tests/test_types/test_exceptions.py tests/test_message.py -q` passes and `uv run python -c "import poop.types.meta as m; print(hasattr(m, '_dunder'))"` prints `False`.

## 4. Integration

- [x] 4.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate "prose-and-dead-code" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `docs(types): comments sit by the code they explain` (1), `refactor(types): dead branches, aliases and ignores go` (2), `refactor: spellings align with their siblings` (3); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
