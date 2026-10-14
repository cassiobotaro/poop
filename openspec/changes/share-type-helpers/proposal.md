# Proposal

## Why

A review of `poop/types/` for pythonic shape found the same few lines
written out in two to six places where a helper the package already has, or
a one-line helper beside it, would hold them once. None of it changes what a
program observes; all of it is where the next drift starts (the `hex`
divergence fixed in `fix-behaviour-leaks` grew out of exactly such a copy).

## What Changes

- **One `_mapping_data(other)`** in `poop/types/mapping_proxy.py` answers the
  raw dict behind a `MappingProxy` or a `_MappingMixin`, or `None`; the six
  copies in `mapping_proxy.py` (`__eq__`, `_merge_data`), `_mapping.py`
  (`__eq__`), `dict.py` (`__ior__`, `update`) and `frozen_dict.py` (`__or__`)
  call it.
- **Set algebra bodies move to `_SetAlgebraMixin`** as `_combined(name,
  others)` and `_asks(name, other)`; `Set` and `FrozenSet` keep one-line
  `def`s per message so the cloaked `__qualname__` stays theirs (the rule
  `_sequence.py` states). `DictKeys.isdisjoint` and `DictItems.isdisjoint`
  share a `_isdisjoint` on `_SetLikeView` the same way.
- **`center` / `ljust` / `rjust`** on `Str` and on `_BytesLikeMixin` go
  through a `_pad(method, selector, width, fillchar)` sibling of `_search`.
- **One `answered(result, receiver, selector, other)`** in
  `poop/types/_message.py` replaces the five "call the dunder, raise
  `binary_refusal` on `NotImplemented`" blocks in `int.py`, `float.py` and
  `complex.py`.
- **One `_own_entry(cls, name)`** in `poop/types/meta.py` walks the MRO's
  dicts for `class_side_named`, `_instance_only` and `_reflected`.
- **One `indexing(...)` context manager** in `poop/types/_at.py` carries the
  `IndexError`/`TypeError` wording that `at_index`, `List.at_put` and
  `ByteArray.at_put` each spell.
- **`_bridge.py` builds a `Dict` through `Dict._wrapping`**, as it builds a
  `FrozenDict`, instead of `Dict()` plus an `at_put` loop.
- **Smaller alignments**: `Zip._generate` releases its sources with `del` as
  `Enumerate` and `_BlockView` do; `_SetAlgebraMixin` derives from `_Mixin`
  so it is cloaked like every other mixin; `Int._integral_value` reads
  `_num_value` instead of re-folding `Boolean`; `Slice._coerce` is
  `_is_absent`; `Range.__init__` resolves its bounds once on raw ints;
  `MappingProxy.__iter__`/`iter`/`reversed`/`__contains__` delegate to the
  wrapped mapping like its other messages; `byte_order` in `_argument.py`
  answers `Literal["big", "little"]` so the two `cast`s in `int.py` go.

Out of scope, and why: hoisting the thirteen identical `includes` and eleven
`len` one-liners onto the iterable mixin — a mixin-defined message reports
`object.includes()` in its arity sentence, which is the `__qualname__` rule
the package keeps on purpose; the same keeps `List.sorted`/`Tuple.sorted`
where they are. The behaviors `fix-behaviour-leaks` changes are not touched
here, so each change can be reviewed on its own.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — source-level refactor; `skip_specs: true`)

## Impact

- `poop/types/`: `mapping_proxy.py`, `_mapping.py`, `dict.py`,
  `frozen_dict.py`, `_set_algebra.py`, `set.py`, `frozen_set.py`,
  `_dict_view.py`, `dict_keys.py`, `dict_items.py`, `string.py`,
  `_bytes_like.py`, `_message.py`, `int.py`, `float.py`, `complex.py`,
  `meta.py`, `_at.py`, `list.py`, `byte_array.py`, `_bridge.py`, `zip.py`,
  `slice.py`, `range.py`, `_argument.py`.
- Tests: existing suites under `tests/test_types/` must pass unchanged;
  `tests/test_cloak.py` or `tests/test_slots.py` gains the mixin-cloak check
  if none covers `_SetAlgebraMixin`.
- Docs: none; no observable behavior or documented decision moves.
