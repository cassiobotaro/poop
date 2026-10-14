# Tasks

## 1. Guards

- [x] 1.1 Add `a_mapping(value, selector)` to `poop/types/_argument.py`, admitting the `_MappingMixin` family and refusing with `#<selector> expects a mapping, got <article class>`, and `translation_table(value, selector)` admitting a mapping or a `List`/`Tuple`/`Str` sequence and refusing with `#translate expects a mapping or a sequence, got <article class>`; verify with tests in `tests/test_types/test_argument.py` for a `Dict`, a `MappingProxy`, an `Int`, a `List` (refused by `a_mapping`, admitted by `translation_table`) that `uv run pytest tests/test_types/test_argument.py -q` passes.

## 2. Str (specs/str-type)

- [x] 2.1 In `poop/types/string.py`, factor `format`'s guard, crossing and rewordings into a private helper and add `format_map(mapping)` calling it with `to_python(a_mapping(mapping, "format_map"))`; verify `uv run poop` on `"{a}-{b}".format_map({"a": 1, "b": 2}).print()` prints `1-2` and `"{a}".format_map(5)` raises `TypeError: #format_map expects a mapping, got an int`.
- [x] 2.2 Add `Str.maketrans` as a `staticmethod` taking one to three arguments (mapping through `a_mapping`, strings through `text_like`), answering `to_poop(str.maketrans(...))`; verify `str.maketrans("abc", "xyz").print()` prints `{97: 120, 98: 121, 99: 122}` and `str.maketrans("ab", "xyz")` raises `ValueError: the first two maketrans arguments must have equal length`.
- [x] 2.3 Add `Str.translate(table)` through `translation_table`; verify `"abc".translate(str.maketrans("abc", "xyz")).print()` prints `xyz`, `"a-b".translate({45: None}).print()` prints `ab`, and `"abc".translate(5)` raises `TypeError: #translate expects a mapping or a sequence, got an int`.
- [x] 2.4 Add tests in `tests/test_types/test_str.py` for every scenario in `specs/str-type/spec.md`; verify `uv run pytest tests/test_types/test_str.py -q` passes.

## 3. Bytes and ByteArray (specs/bytes-type, specs/bytearray-type)

- [x] 3.1 In `poop/types/_bytes_like.py`, add `maketrans(frm, to)` as a `staticmethod` answering `Bytes` from two `bytes_like` arguments, and `translate(table, delete=b"")` answering through `_rewrap`, with `table` `none` or `bytes_like` and `delete` `bytes_like`; verify `b"abc".translate(bytes.maketrans(b"ab", b"xy")).print()` prints `b'xyc'`, `bytearray(b"abc").translate(None, b"b").print()` prints `bytearray(b'ac')`, and `bytearray.maketrans(b"ab", b"xy").class_name().print()` prints `bytes`.
- [x] 3.2 Add tests in `tests/test_types/test_bytes.py` and `tests/test_types/test_byte_array.py` for every scenario in the two spec deltas, including the exact guard sentence for `bytes.maketrans("a", b"x")` and `b"abc".translate(5)`; verify both test files pass.
- [x] 3.3 Update the mixin docstring's message count and the `INFECTIONS.md` sentence that states it; verify `grep -n 'messages' INFECTIONS.md | grep -i mixin` shows the new count.

## 4. Wording and docs

- [x] 4.1 Run `uv run pytest tests/test_no_python_wording.py -q`; route any CPython sentence it reports for `format_map`, `maketrans` or `translate` through the guard it belongs to; verify the sweep passes.
- [x] 4.2 In `INFECTIONS.md`: a paragraph in the Str section (`format_map`, `maketrans`, `translate`, the `to_python` crossing and why), a paragraph in the Bytes section (`maketrans` answers `bytes` on both, `translate` on the mixin), rows in the "Builtin-mirroring method signatures" table, one paragraph under MemoryView for the declined buffer attributes naming `tolist`/`readonly` as the two left for their own change, and one sentence in the exception-budget paragraph for `ExceptionGroup`; verify every snippet added runs under `uv run poop`.

## 5. Integration

- [x] 5.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, and `openspec validate "text-mirrors-complete" --strict`; verify every step exits 0 and coverage stays at or above 95%.
- [x] 5.2 Re-run the mechanical surface diff (every public method of `str`, `bytes`, `bytearray` against the wrapper's MRO) and verify it reports no missing name for the three types.

## Workflow follow-up

- Commit per group (`feat(types): ...` for 2 and 3, `docs:` for 4), hooks passing; archive with `/opsx:archive`, which syncs `str-type` and `bytes-type` as new main specs and adds the two requirements to `bytearray-type`.
