# Tasks

## 1. The wrap

- [x] 1.1 In `poop/types/_descriptor.py`, make `message.__get__` wrap the bound result in a `_MethodBlock` when `type(bound) is MethodType` (either side) or when `self._entry` is a `staticmethod` (either side), leaving a plain function entry read off the class as the raw function; update the module docstring's sentence about staticmethods staying native; verify `uv run poop` on `str.maketrans.print()`, `"".maketrans.print()` and `int.from_bytes.print()` each prints `<block>`, and `str.upper()` still answers `str does not understand #upper — #upper asks an instance; send it to one`.
- [x] 1.2 In `poop/types/block.py`, make `_MethodBlock._identity` answer `(getattr(fn, "__self__", None), getattr(fn, "__func__", fn))` and drop the `cast` and the comment that assumed a `MethodType`; verify `uv run poop` on `(str.maketrans == str.maketrans).print()` prints `True` and `(str.maketrans == bytes.maketrans).print()` prints `False`.

## 2. Tests and docs

- [x] 2.1 Add tests in `tests/test_types/test_block.py` for every scenario in `specs/method-blocks/spec.md`, and flip `test_a_staticmethod_read_off_an_instance_stays_native_as_before` in `tests/test_message_descriptors.py` to assert a `_MethodBlock`, with the generic sweep in that file updated so a `staticmethod` entry expects a `_MethodBlock` too; verify `uv run pytest tests/test_types/test_block.py tests/test_message_descriptors.py tests/test_no_python_wording.py -q` passes.
- [x] 2.2 In `INFECTIONS.md`, add to the Principles bullet "A method is a block, whichever way it is read" one sentence closing the two holes (a `staticmethod` from either side and a `classmethod` from the class answered CPython's raw function, so `str.maketrans.print()` leaked `'function' object has no attribute 'print'` while `get_attr` of the same name answered `<block>`); verify every snippet added runs under `uv run poop`.

## 3. Integration

- [x] 3.1 Run the full gate, `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`, reading the `N passed` line itself, and `openspec validate "method-blocks" --strict`; verify every step exits 0 and coverage stays at or above 95%.

## Workflow follow-up

- One commit (`fix(types): a static or class method read off a wrapper is a block`), code, tests and `INFECTIONS.md` together; push, check CI; archive with `/opsx:archive`, which creates `method-blocks` as a new main spec; commit the archive.
