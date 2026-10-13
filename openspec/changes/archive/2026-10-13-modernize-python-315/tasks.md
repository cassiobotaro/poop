# Tasks

## 1. Block arity under deferred annotations (specs/block-arity)

- [x] 1.1 In `poop/types/block.py`, make `Block._params` call `signature(self._fn, annotation_format=Format.FORWARDREF)` (import `Format` from `annotationlib`); verify `uv run poop` on a file with `f = int.get_attr("from_bytes")` then `f()` prints `block expects 1 to 2 arguments, got 0` instead of a `NameError`.
- [x] 1.2 Add tests in `tests/test_types/test_block.py`: arity refusal for `int.get_attr("from_bytes")()` and `dict.get_attr("fromkeys")()`, keyword refusal for `f(b"\x01", nope=1)`, and an assertion that the message contains none of `Bytes`, `Iterable`, `NoneClass`, `Callable`; verify `uv run pytest tests/test_types/test_block.py` passes and fails when 1.1 is reverted.
- [x] 1.3 Rewrite the `_MethodBlock` docstring to drop the sentence claiming `inspect.signature` evaluates `TYPE_CHECKING`-only annotations, keeping the `cloak` reason; verify `uv run ruff check` and `uv run ty check poop/ tests/` pass.
- [x] 1.4 Add a paragraph to the Block section of `INFECTIONS.md` recording the PEP 649 leak, the reachable path (`get_attr` on a class) and the FORWARDREF decision; verify the snippet it quotes runs as written under `uv run poop`.

## 2. The number guard and from_number (specs/float-type, specs/complex-type)

- [x] 2.1 Add `a_number(value, selector, *, real: bool)` to `poop/types/_argument.py`, answering the unwrapped native (with `Boolean` folded to its int) or raising `mirrors.TypeError` with `#<selector> expects a real number, got <article class>` / `#<selector> expects a number, got <article class>`; verify with tests in `tests/test_types/test_argument.py` covering int, bool, float, complex (both flags), str and list.
- [x] 2.2 Add `Float.from_number` as a classmethod in `poop/types/float.py` answering `wrapped_instance(cls, float(a_number(x, "from_number", real=True)))`; verify `uv run poop` on `float.from_number(3).print()` prints `3.0` and `float.from_number("3")` raises `TypeError: #from_number expects a real number, got a str`.
- [x] 2.3 Add tests in `tests/test_types/test_float.py` for every scenario in `specs/float-type/spec.md`, including the subclass case through a POOP program with `class Money(float)`; verify `uv run pytest tests/test_types/test_float.py` passes.
- [x] 2.4 Add `Complex.from_number` as a classmethod in `poop/types/complex.py` using `a_number(x, "from_number", real=False)`; verify `uv run poop` on `complex.from_number(2.5).print()` prints `(2.5+0j)` and `complex.from_number("1")` raises `TypeError: #from_number expects a number, got a str`.
- [x] 2.5 Add tests in `tests/test_types/test_complex.py` for every scenario in `specs/complex-type/spec.md`; verify `uv run pytest tests/test_types/test_complex.py` passes.
- [x] 2.6 Run `uv run pytest tests/test_no_python_wording.py` and route any CPython sentence the sweep reports for `from_number` through `a_number`; verify the sweep passes.
- [x] 2.7 Document `from_number` in the Float and Complex sections of `INFECTIONS.md` (Python 3.14 origin, classmethod, subclass answer, guard wording) and add both rows to the "Builtin-mirroring method signatures" table; verify every snippet added runs under `uv run poop`.

## 3. ByteArray.resize (specs/bytearray-type)

- [x] 3.1 Add `ByteArray.resize(size)` in `poop/types/byte_array.py` calling `self._value.resize(an_int(size, "resize", "size"))` and answering `none`, letting CPython's `ValueError` for a negative size pass through; verify `uv run poop` on `b = bytearray(b"ab"); b.resize(4); b.print()` prints `bytearray(b'ab\x00\x00')`.
- [x] 3.2 Add tests in `tests/test_types/test_byte_array.py` for every scenario in `specs/bytearray-type/spec.md` (grow, shrink, zero, `True`, str and float refusals, negative size leaves the receiver unchanged, answer is `none`); verify `uv run pytest tests/test_types/test_byte_array.py` passes.
- [x] 3.3 Run `uv run pytest tests/test_no_python_wording.py` and confirm `resize` reports nothing; verify the sweep passes.
- [x] 3.4 Update `INFECTIONS.md`: a `resize` paragraph in the ByteArray section, the `take_bytes` paragraph reworded from "the one 3.15 message" to the pair, and a `resize` row in the method-signature table; verify every snippet added runs under `uv run poop`.

## 4. 3.15 toolchain and docs audit

- [x] 4.1 Confirm the inferred lint and type-check targets: `uv run ruff check --show-settings poop/__init__.py | grep -i target` reports py315 and `uv run ty check poop/ tests/` runs against 3.15 without a `python-version` override; record the two outputs in the commit message and change nothing unless either disagrees.
- [x] 4.2 Confirm `README.md`, `CONTRIBUTING.md`, `AGENTS.md` and `pyproject.toml` all say 3.15 and that `.github/workflows/ci.yml` runs 3.15, 3.15t and 3.16-experimental; verify with `grep -n '3\.1[3-6]' README.md CONTRIBUTING.md AGENTS.md pyproject.toml .github/workflows/ci.yml` showing no version below 3.15 as a requirement.
- [x] 4.3 Run `uv run python -W error::DeprecationWarning -m pytest -q` and confirm the suite is clean on 3.15; verify exit status 0.

## 5. Integration

- [x] 5.1 Run the full gate: `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`; verify coverage stays at or above the 95% floor and `tests/test_doc_counts.py` passes (no validator or example was added).
- [x] 5.2 Run the probe programs for each spec under `uv run poop` one last time (`float.from_number`, `complex.from_number`, `bytearray.resize`, `int.get_attr("from_bytes")()`) and compare against the scenarios; verify each prints the sentence its spec states.

## Workflow follow-up

- Commit in atomic commits per group (hooks must pass; never `--amend`), with the attribution line the session requires.
- Archive the change after review; `openspec archive` will create the four main specs from the deltas.
