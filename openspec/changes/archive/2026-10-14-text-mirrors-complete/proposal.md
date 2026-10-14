# Proposal

## Why

A mechanical diff of every mirrored builtin's public methods against its
wrapper leaves exactly three names missing on the text types: `str.format_map`,
and `maketrans`/`translate` on `str`, `bytes` and `bytearray`. They are not
3.14/3.15 additions, so the modernization left them out on purpose; they are
the last gap between "POOP types pass as Python builtins" and the surface a
reader on 3.15 expects, and `"{a}".format_map(d)` is the message-shaped
spelling of what POOP today forces into a `**d` spread.

## What Changes

- **`Str.format_map(mapping)`**: the template engine `format` already runs,
  fed by a POOP mapping (`Dict`, `FrozenDict`, `MappingProxy`). Field access
  (`{0.attr}`, `{0[key]}`) stays refused by the existing guard; a missing name
  is worded as `format` already words it; a non-mapping is refused by a new
  shared guard, `a_mapping`, where CPython says `'int' object is not
  subscriptable`.
- **`str.maketrans(...)`** (static, as CPython's): the one-argument mapping
  form and the two/three-argument string form, answering a `Dict` of `Int`
  to `Int`, `Str` or `none`. **`Str.translate(table)`** takes a POOP mapping
  or sequence and answers a `Str`; the table crosses to Python through
  `to_python`, since a `Dict` holds `Int` keys and CPython looks ordinals up
  as raw ints.
- **`bytes.maketrans(frm, to)`** / **`bytearray.maketrans`** (static, both
  answering a `Bytes` of 256, as CPython does) and **`translate(table,
  delete=b"")`** on both, answering the receiver's own kind. They live in
  `_BytesLikeMixin`, which holds every message the two answer alike.
- **Two decisions recorded in `INFECTIONS.md`**, no code: the `memoryview`
  buffer attributes (`shape`, `strides`, `itemsize`, `format`, `ndim`, `cast`,
  `obj`, `release`, `toreadonly`, the contiguity flags) stay out, because POOP
  has only one-dimensional byte views and keeps buffer-protocol vocabulary out
  by an earlier decision; and `ExceptionGroup` stays out of the exception
  mirror, because nothing in the language produces a group and `except*` is
  already refused.

Out of scope, and why: `MemoryView.tolist` and `readonly` (the maintainer
chose to leave them; they can come as their own small change), and any change
to how `format` itself words its refusals.

## Capabilities

### New Capabilities
- `str-type`: the messages a `Str` and the `str` class answer, mirroring
  CPython's `str` in POOP's wording. This change adds `format_map`,
  `maketrans` and `translate`.
- `bytes-type`: the messages a `Bytes` and the `bytes` class answer. This
  change adds `maketrans` and `translate`.

### Modified Capabilities
- `bytearray-type`: adds `maketrans` and `translate` (new requirements; the
  existing `resize` requirements are untouched).

## Impact

- `poop/types/string.py` (`format_map`, `maketrans`, `translate`),
  `poop/types/_bytes_like.py` (`maketrans`, `translate`),
  `poop/types/_argument.py` (`a_mapping`, and a `translation_table` guard for
  the mapping-or-sequence case).
- Tests: `tests/test_types/test_str.py`, `test_bytes.py`, `test_byte_array.py`,
  `test_argument.py`. The wording sweep covers the new messages automatically.
- Docs: `INFECTIONS.md` (Str and Bytes sections, the mixin's message count,
  the method-signature table, one paragraph each for the two declined
  surfaces). `README.md` counts are unchanged.
