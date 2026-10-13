# Design

## Context

See proposal.md - Why. The facts the approach rests on, all verified on the
3.15.0 interpreter uv resolves for this repository:

- `requires-python = ">=3.15"`, `.python-version` is `3.15`, CI runs 3.15,
  3.15t and 3.16 (experimental). The suite passes with `DeprecationWarning`
  raised as an error. `ruff check --preview --select UP --target-version py315`
  reports nothing: there is no pre-3.15 syntax left to upgrade.
- The language side already covers 3.14/3.15: t-strings and `lazy import` are
  refused with their own sentences, `frozendict` and `sentinel` are wrapped,
  `bytearray.take_bytes` and the `math.integer` six are mirrored. A mechanical
  diff of every mirrored builtin's public methods against its wrapper's MRO
  leaves exactly three 3.14/3.15 additions missing: `float.from_number`,
  `complex.from_number`, `bytearray.resize`.
- `Block._params` calls `inspect.signature(self._fn)` and catches `TypeError`
  and `ValueError`. Under PEP 649 (3.14+) `signature` evaluates the callee's
  annotations lazily and raises `NameError` for a name declared only under
  `TYPE_CHECKING`, which is how `poop/types/` declares most of its annotations.
  `_MethodBlock` bypasses `_params`, so the only reachable path is a block made
  by `_as_block` from `get_attr` on a *class*; there it leaks
  (`int.get_attr("from_bytes")()` -> `NameError: name 'Bytes' is not defined`).
- Conventions that bind every addition: a method mirrors the Python name; a
  void mutator answers `none`; every argument refusal goes through a guard in
  `_argument.py` so the sentence reads the same on every receiver; the wording
  sweep sends every public message wrong-typed arguments and fails on any
  CPython sentence; `INFECTIONS.md` is updated in the same commit.

## Goals / Non-Goals

**Goals:**
- Every message CPython 3.14/3.15 added to a type POOP mirrors exists on the
  wrapper, follows CPython on every edge, and refuses a wrong argument in the
  shared wording.
- No path from user code reaches an interpreter-internal `NameError` through
  signature introspection.
- The toolchain and the three documents say 3.15 consistently, and the
  catalogue stops calling `take_bytes` the only 3.15 message.

**Non-Goals:**
- Mirroring methods older than 3.14 that happen to be missing
  (`str.format_map`, `maketrans`/`translate`, the `memoryview` buffer
  attributes). Each is its own proposal.
- Widening the exception mirror (`ExceptionGroup`, `BufferError`): the table of
  seventeen is a documented decision, and a `bytearray` mutated while a
  `memoryview` exports it already answers a generic `Exception` on every
  mutator today; `resize` joins that behavior rather than fixing it.
- Changing `_MethodBlock`'s refusal, which stays CPython's reworded by `cloak`.
  Only the docstring's now-false reason changes.
- Adopting 3.15 stdlib for its own sake (`string.templatelib`,
  `concurrent.interpreters`, `compression.zstd`): nothing in `poop/` has a use
  for them.

## Decisions

**1. `from_number` is a classmethod answering through the class it was sent to.**
`Float.fromhex` and `Bytes.fromhex` already use `wrapped_instance(cls, ...)`,
so a user `class Money(float)` answers a `Money`, as CPython does. `from_number`
follows the same shape rather than returning `Float(...)` directly.
*Alternative*: a plain method on the instance side. Rejected: CPython's is a
classmethod and the class side (`PoopMeta`) already resolves classmethods.

**2. One new argument guard, `a_number`, with a `real` flag, in `_argument.py`.**
`float.from_number` accepts int/bool/float; `complex.from_number` also
accepts complex. Both refuse everything else with
`#from_number expects a real number, got a str` / `#from_number expects a
number, got a str`. One guard with two spellings keeps the refusal identical on
both receivers, which is the reason `_argument.py` exists; the native check is
`isinstance(raw, numbers.Real)` / `numbers.Complex` on the unwrapped payload,
with `Boolean` folded to its integer as `_searched` already does.
*Alternative*: catch CPython's `TypeError` and reword. Rejected: `must be real
number, not str` carries no call, dunder or operator, so the sweep's patterns
would not see a regression, and a guard is the documented pattern.

**3. `resize` goes through `an_int` for the size and keeps CPython's `ValueError`
for a negative one.** `an_int(size, "resize", "size")` gives
`#resize's size must be an int, got a str`, the sentence every other integer
argument answers. `Can only resize to positive sizes, got -1` names no
construct POOP forbids, the same argument `take_bytes` makes for its
`IndexError`, so it passes through unreworded. The method answers `none` under
the void-mutator rule.

**4. `_params` reads the signature with `annotation_format=Format.FORWARDREF`.**
`inspect.signature(fn, annotation_format=annotationlib.Format.FORWARDREF)`
answers the parameters without evaluating annotations, so an undefined
`TYPE_CHECKING` name becomes a `ForwardRef` instead of a `NameError`; `_params`
only reads `kind`, `default` and `name`, never the annotation. This is the 3.14
API designed for exactly this case and is the only change needed.
*Alternative A*: also catch `NameError` in `_params`. Rejected: it would turn
the arity sentence into `block does not accept 0 arguments` (the degraded
path) when FORWARDREF gives the true counts.
*Alternative B*: evaluate with `Format.STRING`. Rejected: equivalent for the
fields read, and FORWARDREF is the documented "do not fail" mode.

**5. `_MethodBlock` keeps CPython's arity refusal; its docstring changes.**
The docstring gives two reasons for not rewording: `cloak` has already worded
the message's name, and `inspect.signature` evaluates annotations. The second
is no longer true once `_params` uses FORWARDREF. The first still holds and is
the one that matters (the rewording would replace `str.upper()` with the word
`block`), so behavior is unchanged and only the stale sentence goes.

**6. The audit is verification plus one catalogue edit, not configuration.**
ruff and ty both derive their target from `requires-python`; adding an explicit
`target-version` would be a second place to keep in step, the drift
`test_doc_counts.py` was written against. The audit confirms the inferred
targets with the tools' own output and touches only `INFECTIONS.md`, where
`take_bytes` is called "the one 3.15 message on a type POOP mirrors" and
`resize` now makes two.

## Risks / Trade-offs

- [The wording sweep may surface CPython sentences from `from_number`/`resize`
  that this design did not anticipate] -> the sweep runs in the ordinary test
  run; any new sentence is routed through the guard it belongs to before the
  commit, as the catalogue documents for the other 47.
- [`numbers.Real` accepts user classes registered as Real, and `Boolean` is not
  a Python `bool` subclass] -> the guard reads the unwrapped payload, where
  `Boolean` folds to an `int`, and POOP programs cannot register ABCs
  (`no_import`), so the only payloads are the wrappers' own natives.
- [FORWARDREF changes nothing for callables that carry no signature at all]
  -> those still raise `ValueError`/`TypeError` and keep the existing degraded
  path; the fix is additive.
- [`resize` on a `ByteArray` with a live `MemoryView` answers a raw
  `BufferError` surfaced as `Exception`] -> same as `append`/`clear` today;
  recorded as a non-goal, candidate for its own proposal.
