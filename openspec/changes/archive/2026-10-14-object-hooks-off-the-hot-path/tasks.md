# Tasks

## 1. The descriptor

- [x] 1.1 Add the `message` descriptor (in `poop/types/_message.py` or a new `poop/types/_descriptor.py`, whichever avoids a cycle with `block`): `__slots__ = ("__func__",)`, `__get__(None, owner)` answers the entry's own class-side binding, `__get__(inst, owner)` binds through the entry and answers `_MethodBlock(bound)` (late-bound, as `object.py` does) when `type(bound) is MethodType`, else the bound value; install it in `PoopMeta.__new__` over every namespace entry whose `getattr(entry, "__func__", entry)` is a `FunctionType` and whose name `is_message` accepts, and in `_Mixin.__init_subclass__` over `vars(cls)`; verify `uv run pytest tests/test_types/test_block.py tests/test_types/test_meta.py -q` passes with `Object.__getattribute__` still in place.
- [x] 1.2 Make `_instance_only` and `_reflected` in `poop/types/meta.py` unwrap through `__func__`, and confirm `_rename_own_functions` in `_cloak.py` needs no change; verify `str.upper()` under `uv run poop` still answers `str does not understand #upper — #upper asks an instance; send it to one` and `int.from_bytes(b"\x05")` still answers `5`.
- [x] 1.3 Delete `Object.__getattribute__` (the `if not TYPE_CHECKING` block keeps `__getattr__`), remove `_METHOD_BLOCK`/`_install_method_block`/`_method_block` from `object.py` and the install line from `block.py` if the descriptor binds `_MethodBlock` itself, and update the `class_side.__get__` comment that cites the hook; verify `uv run pytest tests/test_types/test_block.py tests/test_types/test_object.py tests/test_no_python_wording.py -q` passes.

## 2. The assignment refusal

- [x] 2.1 Move the sentence into `poop/types/_message.py` as `holds_no_state(class_name: str) -> str`, add `_NO_STATE` to `poop_message`, make `_holds_no_state` in `object.py` compose through it, and delete `Object.__setattr__`; verify `uv run poop` on `"abc".x = 5` answers `AttributeError: str is a value — it holds no state of its own; only an object of a class you defined can be given one`, and a `Try` handler's `e.message()` for the same assignment prints the same sentence.
- [x] 2.2 Move any test asserting the assignment refusal with `pytest.raises(..., match=)` at the Python level to assert through `poop_message` or the interpreter; verify `uv run pytest tests/test_types/test_object.py tests/test_slots.py -q` passes.

## 3. Guards and measurement

- [x] 3.1 Add `tests/test_message_descriptors.py` with the assertions design.md decision 5 lists, including the user-class method and `super()` case; verify it passes, and that re-adding a one-line `__getattribute__` to `Object` makes it fail.
- [x] 3.2 Extend `tests/test_hot_paths_bind_late.py`'s operations with `Int(3)` construction and a `Str("ab")._value` read if they are not already covered, since the paths changed; verify it passes.
- [x] 3.3 Run the micro-timing script (the exploration's: `(5).abs()`, `a._value`, `Int(3)`, `Int + Int`, plus the nine from `hot-path-imports`) against `main` before 1.1 and the tree after 2.2, same session, and record both columns under `## Measured` in `design.md`; verify `Int + Int` and `Int(3)` improve by at least 30 %, `(5).abs()` by at least 25 % and `a._value` by at least 40 %, and stop to report if they do not.
- [x] 3.4 In `INFECTIONS.md`: rewrite the Principles bullet "A method is a block, whichever way it is read" so it names the descriptor rather than `Object.__getattribute__`, and add a paragraph to the Object section recording the two hooks, why each existed, the measurement, and the rule (no Python-level hook on `Object`'s instance side; a per-value refusal is reworded in `poop_message`); verify every snippet added runs under `uv run poop`.

## 4. Integration

- [x] 4.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, and `openspec validate "object-hooks-off-the-hot-path" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- Commits per group: `perf(types): messages are descriptors; Object drops __getattribute__` (1), `perf(types): the assignment refusal is reworded in poop_message; Object drops __setattr__` (2), `test: the Object hooks stay off; record the measurement` (3, with the INFECTIONS slice); push, check CI; archive with `/opsx:archive` (no delta specs); commit the archive.
