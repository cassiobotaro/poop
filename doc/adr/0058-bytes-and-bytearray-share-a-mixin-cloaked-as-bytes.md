# 58. `Bytes` and `ByteArray` share a mixin cloaked as `bytes`

Date: 2026-10-04

## Status

Accepted

## Context

`Bytes` and `ByteArray` answer most of their messages alike: 46 messages had identical bodies once the class name was normalised, about 290 lines written twice. CPython makes the same move with `bytes_methods.c`.

A shared mixin has to be cloaked under some name, because a wrong-arity call blames the function's qualname. The other shared mixins are cloaked as `object`. For this pair, `object.upper()` would be true for neither receiver, while `bytes.upper()` is true for one and close for the other; the pair is already one group under that name in `_eq_group` and `_order_group`.

The language keeps the two classes interchangeable, and places that treated them as strangers contradicted it. `==` crossed through `_eq_group` (the `"bytes"` group `_value_eq.py` declares), `+` crossed through its guard and `includes` through the subsequence search, but `b"ab" < bytearray(b"ac")` answered `bytes does not understand #< with a bytearray`, in both directions. `startswith` and `endswith` exist on `Str`, `Bytes` and `ByteArray`, and with `or` banned a tuple of affixes is the only way to ask `s.startswith("a") or s.startswith("b")`. Only `Str` mapped a POOP `Tuple` to a Python one, so `b"ab".startswith((b"a", b"z"))` answered `startswith first arg must be bytes or a tuple of bytes, not tuple`, contradicting a reader who did pass a tuple.

## Decision

`_BytesLikeMixin` (`poop/types/_bytes_like.py`) holds every message `Bytes` and `ByteArray` answer alike. Each class supplies `_rewrap`, which turns a raw result back into its own builtin kind, and keeps what differs: construction, `+`, `fromhex`, `hex` (a `ByteArray` separator is converted for `bytearray.hex`), hashing, its iterator and, on `ByteArray`, the mutators.

The mixin is cloaked as `bytes`, so `bytearray(b"a").upper(1)` reads `bytes.upper() takes 1 positional argument…`.

The pair is one kind wherever an operand is checked. The four ordering dunders on each side take the same `Bytes | ByteArray` operand their neighbouring `__add__` does, so a mixed `sorted` works. `affix_needle` (`poop/types/_affix.py`) is shared by `Str`, `Bytes` and `ByteArray`, since only its scalar branch was ever string-specific; the affix and each member of a tuple go through `text_like`, so a wrong-typed one is refused as `#startswith expects a str or a tuple of str, got an int`.

## Consequences

A message added to the pair is written once. A foreign operand to an ordering dunder still answers the faithful `TypeError`.

The cloak is only right where one name is close for both receivers. `List` and `Tuple` share less and share it differently: `_SequenceMixin` (`poop/types/_sequence.py`) holds the dunders the two spell identically (`__len__`, `__iter__`, `__contains__`, `__mul__`, `__rmul__`) and the bodies of `index` and `print` as private helpers. The *messages* stay on each class as one-line `def`s, so `tuple.index()` stays `tuple.index()` in a wrong-arity report. `Set` and `FrozenSet` follow the same rule under `_SetAlgebraMixin`. Within one class a family follows it too: `find`, `index`, `count`, `rfind` and `rindex` stay five one-line `def`s on `Str` and on `_BytesLikeMixin`, each handing its native bound method to `_search`, and `startswith`/`endswith` hand theirs to `_affix`.
