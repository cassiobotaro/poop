# Tasks

## 1. Mappings

- [ ] 1.1 Add `_mapping_data(other) -> dict[Object, Object] | None` to `poop/types/mapping_proxy.py` and route `MappingProxy.__eq__`, `_merge_data`, `_MappingMixin.__eq__` (`_mapping.py`), `Dict.__ior__` and `Dict.update` (`dict.py`) and `FrozenDict.__or__` (`frozen_dict.py`) through it; verify `uv run pytest tests/test_types/test_dict.py tests/test_types/test_frozen_dict.py tests/test_types/test_mapping_proxy.py tests/test_types/test_value_eq.py -q` passes.
- [ ] 1.2 Make `MappingProxy.__iter__`, `iter`, `reversed` and `__contains__` delegate to the wrapped mapping and drop the `DictKeyIterator`/`DictReverseKeyIterator` imports there; verify the mapping_proxy and dict_view tests pass.
- [ ] 1.3 In `poop/types/_bridge.py`, build the `Dict` registration through `Dict._wrapping({to_poop(k): to_poop(v) …})`; verify `uv run pytest tests/test_types/test_bridge.py tests/test_bridge_types.py -q` passes.

## 2. Sets

- [ ] 2.1 Derive `_SetAlgebraMixin` from `_Mixin` (`poop/types/_set_algebra.py`), add `_combined(name, others)` and `_asks(name, other)` to it, reduce the seven messages on `Set` and `FrozenSet` to one-line `def`s, and share `_isdisjoint` on `_SetLikeView` for `DictKeys`/`DictItems`; verify the set, frozen_set, dict_keys, dict_items and iterator tests pass, that `uv run poop` on `{1}.union(1, 2)` still names `set.union` in its refusal, and add a check to `tests/test_cloak.py` that every `_Mixin` subclass under `poop/types/` answers a cloaked `__name__`.

## 3. Text and numbers

- [ ] 3.1 Add `_pad(method, selector, width, fillchar)` beside `_search` in `Str` (`poop/types/string.py`) and in `_BytesLikeMixin` (`poop/types/_bytes_like.py`) and make `center`/`ljust`/`rjust` one-liners; verify the str, bytes and byte_array tests pass.
- [ ] 3.2 Add `answered(result, receiver, selector, other)` to `poop/types/_message.py` and use it at the five `NotImplemented` sites in `int.py`, `float.py` and `complex.py`; make `Int._integral_value` read `_num_value`; verify `uv run pytest tests/test_types/test_int.py tests/test_types/test_float.py tests/test_types/test_complex.py tests/test_message.py -q` passes.
- [ ] 3.3 Annotate `byte_order` in `poop/types/_argument.py` as `Literal["big", "little"]` and drop the two `cast`s in `int.py`; verify `uv run ty check poop/ tests/` passes.

## 4. Sequences, slices and the class side

- [ ] 4.1 Add the `indexing(receiver, items, index, selector)` context manager to `poop/types/_at.py` and use it in `at_index`, `List.at_put` and `ByteArray.at_put`; verify `uv run pytest tests/test_types/test_at.py tests/test_types/test_list.py tests/test_types/test_byte_array.py -q` passes and the two refusal sentences are byte-identical to before (grep them in the tests).
- [ ] 4.2 Make `Slice._coerce` use `_is_absent`, resolve `Range.__init__`'s bounds once on raw ints, and release `Zip._generate`'s sources with `del`; verify the slice, range and zip tests pass.
- [ ] 4.3 Add `_own_entry(cls, name)` to `poop/types/meta.py` and rewrite `class_side_named`, `_instance_only` and `_reflected` over it; verify `uv run pytest tests/test_types/test_meta.py tests/test_types/test_exceptions.py tests/test_message_descriptors.py -q` passes.

## 5. Integration

- [ ] 5.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line, and `openspec validate "share-type-helpers" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `refactor(types): one mapping-operand helper` (1), `refactor(types): set algebra shares its bodies` (2), `refactor(types): padding, operator refusals and byte order` (3), `refactor(types): indexing, bounds and the class side's MRO walk` (4); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
