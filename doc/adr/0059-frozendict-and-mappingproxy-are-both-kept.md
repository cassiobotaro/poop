# 59. `FrozenDict` and `MappingProxy` are both kept

Date: 2026-10-09

## Status

Accepted

## Context

Python 3.15 added `frozendict` (PEP 814), the half-pair that `frozenset` → `FrozenSet` left open. POOP already had a `MappingProxy`, and both are read-only mappings, so folding one into the other was the alternative.

CPython has both, for different jobs. A `mappingproxy` is a live read-only *view* of a mapping that may change under it (a class's `__dict__`, a view's `.mapping`). A `frozendict` is a *value*, which is why one hashes and the other cannot. Folding one into the other would lose either the liveness or the hash.

## Decision

POOP keeps both. `FrozenDict` (`poop/types/frozen_dict.py`) is `Dict`'s read side plus a hash, and every edge is CPython's:

- It is not a `dict` subclass (`fd.is_instance(dict)` is false). It is a sibling of `Dict` under `_MappingMixin`, the mapping twin of `_BytesLikeMixin`.
- Equality ignores insertion order and crosses the kinds both ways (`frozendict(a=1) == {"a": 1}`), which `_ValueEqMixin`'s `"mapping"` group states once for both. The hash is order-blind like the equality.
- `copy` answers the receiver, and `frozendict(fd)` answers `fd` itself. `fd | d` is a `FrozenDict` and `d | fd` a `Dict`, the left operand's kind. Every site that asked `isinstance(x, Dict)` asks for the mixin, so `**fd`, `{**fd}`, `dict(fd)`, `d.update(fd)` and `d |= fd` all take it.
- Its views are the dict's: `fd.keys()` is a `dict_keys` whose `mapping()` is a `mappingproxy(frozendict(...))`.
- A write (`update`, `at_put`, `pop`, …) is refused as `does not understand`, with the hint 3.15 gives for `frozendict.update`, `did you mean to use a dict?`.

The proxy wraps any mapping, as `types.MappingProxyType` does, and the views take any mapping.

## Consequences

Neither type needed a second copy of anything. The mixin carries the shared read side, and the proxy and views accept a `FrozenDict` as they accept a `Dict`.
