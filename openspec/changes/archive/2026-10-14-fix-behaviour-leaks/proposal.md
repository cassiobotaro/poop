# Proposal

## Why

A review of `poop/` for pythonic shape turned up nine places where the code
does something a program can observe and that is wrong: a sum that mutates
its first element, a `slice(*xs)` folded at parse time, a `get_attr` whose
`*default` lets CPython's `getattr` sentence through, a validator that skips
parameter annotations, a `dict(**x)` fold that predates the general `**`
rewrite and diverges from CPython, a `hex` separator check that drifted
between the two byte wrappers, a `.slice(slice, stop)` call that drops its
bounds in silence, a docstring the transformers turn into a per-call `Str`
allocation, and a REPL that leaves `sys.ps1` behind. Each is small and each
has a test-shaped reproduction, so they go together as one change.

## What Changes

- **`sum` adds with the binary operator**, never in place: `[a, b].sum()`
  no longer answers `a` itself nor extends it, and `xs.sum(start)` leaves
  `start` untouched, as `builtins.sum` does.
- **`slice(*xs)` is no longer folded at parse time.** The one-argument rule
  (`slice(stop)` is `slice(None, stop, None)`) moves into the runtime
  converter, where the argument count is known. The `call_args` hook on
  `BuiltinRewriter`, which existed only for this fold, goes with it.
- **`get_attr` takes one optional default**, on the instance side and the
  class side alike; a third positional argument is refused the way every
  message refuses too many arguments, naming `get_attr` and never `getattr`.
- **`no_poop_prefix` visits parameter annotations**: `def m(self, x:
  _poop_int)` is refused like `-> _poop_int` already is.
- **`dict(a, k=v, **b)` is no longer folded into a merge.** The general `**`
  rewrite (`VarargsTransformer`) already unwraps a splat's keys at every call
  site, so the special case is removed and `dict(**{1: 2})` and
  `dict(a, x=1, **{"x": 2})` answer what every other call answers.
  `FrozenDictTransformer` loses its copy of the same fold.
- **`hex` has one body** on the byte-like mixin, so `bytearray` refuses a
  `bytearray` separator exactly as `bytes` does and as CPython does.
- **`.slice(slice, stop)` is refused**: a sequence's `slice` takes a `Slice`
  or bounds, not both.
- **A docstring stays a docstring.** `StrTransformer` leaves the first string
  statement of a module, class or function body as a raw constant, so CPython
  stores it as `__doc__` and no `Str` is built on each call; the variadic
  prologue `VarargsTransformer` inserts goes after it, not before.
- **The REPL restores `sys.ps1` / `sys.ps2` by deleting them** when they did
  not exist before the session, so `hasattr(sys, "ps1")` answers what it
  answered before.

Out of scope, and why: the shared-helper refactors the same review found
(`share-type-helpers`, `trim-transformers-validators`) and the prose and
dead-code cleanup (`prose-and-dead-code`) change no behavior and are their
own changes, so that this one can be reviewed as nine reproductions and nine
fixes. The wording of a wrong-arity call to a message (`object.get_attr()
takes from 2 to 3 positional arguments but 4 were given`) is CPython's with
the cloaked name, as it is for every message today, and is not reworded here.

## Capabilities

### New Capabilities

- `collection-iterable-methods`: the messages `_IterableMixin` gives every
  collection (`sum` here; the section "Collection iterable methods" of
  INFECTIONS.md).
- `slice-transformer`: how `slice(...)` calls are rewritten and built.
- `slice-type`: the `Slice` wrapper and the `slice` message of the sequences.
- `object-type`: the protocol every object answers (`get_attr` here).
- `no-poop-prefix-validator`: where a `_poop_` name is refused.
- `dict-transformer`: how `dict(...)` calls are rewritten and built.
- `str-transformer`: which string constants are wrapped.
- `varargs-transformer`: where the variadic prologue lands.
- `repl`: the process state the REPL touches and restores.

### Modified Capabilities

- `bytearray-type`: adds a requirement for the separator `hex` accepts (no
  existing requirement changes).

## Impact

- `poop/types/_iterable_mixin.py` (`sum`), `poop/types/object.py` and
  `poop/types/meta.py` (`get_attr`), `poop/types/_bytes_like.py`,
  `poop/types/bytes.py`, `poop/types/byte_array.py` (`hex`),
  `poop/types/slice.py` (`_resolve_py_slice`).
- `poop/transformers/slice.py`, `poop/transformers/base.py` (`call_args`),
  `poop/transformers/dict.py`, `poop/transformers/frozen_dict.py`,
  `poop/transformers/string.py`, `poop/transformers/varargs.py`,
  `poop/transformers/_registry.py` (the ordering comment on
  `SliceTransformer`).
- `poop/validators/no_poop_prefix.py`; `poop/repl.py`.
- Tests under `tests/test_types/`, `tests/test_transformers/`,
  `tests/test_validators/test_no_poop_prefix.py`, `tests/test_repl.py`.
- `INFECTIONS.md`: the Slice, Dict and `_poop_*` sections; `README.md` is
  unchanged (no validator or example count moves).
