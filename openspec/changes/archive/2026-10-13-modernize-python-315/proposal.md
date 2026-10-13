# Proposal

## Why

POOP declares itself a Python 3.15 interpreter and already runs on it, yet
the 3.14/3.15 release pair left three gaps a reader on 3.15 will hit: two
messages CPython added to types POOP mirrors are missing (`float.from_number`,
`complex.from_number`, `bytearray.resize`), and PEP 649's deferred annotations
turned one of POOP's own introspection calls into a `NameError` leak
(`int.get_attr("from_bytes")()` answers `name 'Bytes' is not defined`). Closing
them now, while the backlog is empty, keeps "a Python 3.15 interpreter" a true
sentence rather than a target.

## What Changes

- **New messages on mirrored types** (Python 3.14/3.15 surface):
  - `Float.from_number(x)` and `Complex.from_number(x)`, class-side, answering
    the receiver's class (a subclass answers itself, as CPython does), with a
    non-number refused in POOP's wording rather than CPython's
    `must be real number, not str`.
  - `ByteArray.resize(size)`: grows with zero bytes or truncates in place and
    answers `none`; a non-integer size is refused by the shared integer guard;
    a negative size keeps CPython's `ValueError`, which names no construct POOP
    forbids.
- **Block arity under deferred annotations**: a block built from a method or
  classmethod whose annotations are declared under `TYPE_CHECKING` no longer
  leaks `NameError` when called with the wrong arguments. The refusal is
  POOP's arity sentence, as for any other block. The stale reasoning in the
  method-block docstring that cites this failure is rewritten.
- **3.15 toolchain and docs audit**: confirm the version pins, lint target,
  type-checker target, CI matrix (3.15, 3.15t, 3.16-experimental) and the
  three documents agree on 3.15; record `resize` beside `take_bytes` in the
  catalogue, which currently calls `take_bytes` "the one 3.15 message".

No breaking changes. Every message added is one CPython 3.15 has; nothing is
renamed or removed.

Out of scope, recorded so the decision is visible: `str.format_map`,
`str`/`bytes.maketrans` and `translate`, the `memoryview` buffer attributes,
and `ExceptionGroup`. None of them is a 3.14/3.15 addition; the exception
budget is a documented choice of seventeen, and the rest are candidates for
their own proposals, not for a modernization.

## Capabilities

### New Capabilities
- `float-type`: the messages a `Float` and the `float` class answer, mirroring
  CPython's `float` in POOP's wording. This change adds `from_number`.
- `complex-type`: the messages a `Complex` and the `complex` class answer,
  mirroring CPython's `complex`. This change adds `from_number`.
- `bytearray-type`: the messages a `ByteArray` answers, mirroring CPython's
  `bytearray`. This change adds `resize`.
- `block-arity`: how a block refuses a call with the wrong arguments, including
  a block made from a method or classmethod of a builtin wrapper.

### Modified Capabilities
<!-- none: the project has no specs yet -->

## Impact

- `poop/types/float.py`, `poop/types/complex.py`, `poop/types/byte_array.py`:
  one new method each.
- `poop/types/_argument.py`: one new guard for "a real number" / "a number",
  so both `from_number` messages read the same refusal.
- `poop/types/block.py`: `_params` reads the signature with
  `annotation_format=Format.FORWARDREF`; the `_MethodBlock` docstring loses
  the sentence about `inspect.signature` evaluating annotations.
- Tests: `tests/test_types/test_float.py`, `test_complex.py`,
  `test_byte_array.py`, `test_block.py`. The wording sweep
  (`tests/test_no_python_wording.py`) picks up the new messages automatically
  and will fail on any CPython sentence they leak.
- Docs: `INFECTIONS.md` (Float, Complex, ByteArray sections and the
  `take_bytes` paragraph; the Block section for the arity fix). `README.md`
  counts are unchanged: no validator or example is added.
- No new dependencies. `annotationlib.Format` is stdlib since 3.14.
