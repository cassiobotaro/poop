# Proposal

## Why

`to_poop` in `poop/types/_bridge.py` is declared through sixteen overloads so
that callers get the POOP class back (`Int.__pow__` is typed `Int | Float |
Complex` on their strength). Four of them cannot be reached: `dict[object,
object]`, `list[object]`, `set[object]` and `frozendict[object, object]` are
invariant in their type parameters, so a `dict[int, int]` or a `list[str]`
matches none of them and falls through to the final `object -> object`
overload. `tuple` and `frozenset` escape because they are covariant. The
first caller to hand the bridge a typed container was `Str.maketrans`, which
had to add `cast("Dict", to_poop(table))` with a comment explaining the
overload it could not reach; the next caller would add the next cast.
Checked with ty 0.0.87: `assert_type(to_poop(d), Dict)` on a `d: dict[int,
int]` fails today, and passes with the parameters widened to `Any`.

## What Changes

- **The four invariant overloads take `Any` parameters**: `dict[Any, Any]`,
  `list[Any]`, `set[Any]`, `frozendict[Any, Any]`; `tuple[Any, ...]` and
  `frozenset[Any]` follow for consistency even though covariance already
  saved them. The concrete classes stay — a `Mapping` or `Sequence` would
  promise a `List` for a `str`, a `range` or a `MappingProxyType` that
  `_to_poop` never converts. The bridge's module docstring gains the reason,
  so the next reader does not "tighten" them back to `object`.
- **`Str.maketrans` drops its `cast`** and the comment that justified it.
- **A static guard**: a test file calling `typing.assert_type` on `to_poop`
  of *typed variables* of each container kind (`dict[int, int]`, `list[int]`,
  `set[str]`, `frozendict[str, int]`, `tuple[int, int]`, `frozenset[str]`,
  and `str.maketrans("a", "b")`), asserting the POOP class. ty checks it in
  the full gate; at runtime it is a no-op. Literals do not do: ty infers a
  `{1: 2}` literal against the parameter bidirectionally and the assertion
  passes even on the broken overloads, so the test must go through declared
  variables.

No observable behavior changes: the dispatcher behind the overloads is
untouched, every message answers what it answered. `skip_specs` is declared.

Out of scope, and why: `to_python`, declared `-> object` on purpose (its
docstring says why: it crosses out of the language and nothing in `poop/`
reads a member back); the `_to_poop` late getter in `int.py`, which declares
its own return type and never consulted the overloads; a `Mapping`/`Sequence`
widening, rejected above.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — typing-only; `skip_specs: true`)

## Impact

- `poop/types/_bridge.py` (six overload signatures, one docstring paragraph),
  `poop/types/string.py` (one `cast` and its comment removed).
- Tests: `tests/test_bridge_types.py` (new; checked by ty, run by pytest as a
  no-op).
- Docs: none beyond the docstring. `README.md` and `INFECTIONS.md` are
  unchanged: the catalogue records language decisions, and this is a type
  annotation.
