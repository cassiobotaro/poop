# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 3. Once every
item has been implemented and deleted, numbering starts over at 1.

### 1. No imports inside test functions

`CONTRIBUTING.md`: "All imports live at the top of the module. Use a
function-local `import` only to break a circular import." `poop/` now holds to
that, and ruff's `PLC0415` enforces it there. `tests/` is exempt in
`pyproject.toml`, and it uses the exemption heavily: 333 imports inside test
functions, across 52 files.

```python
def test_map_ne_is_identity_based() -> None:
    from poop.types.boolean import false, true
    from poop.types.list import List
    ...
```

None of them breaks a cycle. A test module is imported by pytest after the
whole `poop` package has loaded, so it has no cycle to break. Nothing in
`tests/` reloads a module or edits `sys.modules` either: a local import there
never controls *when* something is imported. The 333 are habit:

- 288 import from `poop` — `test_boolean.py` alone repeats 32 of them.
- 45 import the standard library or `pytest`, including `import pytest` inside
  a test in a module that already imports it at the top (`test_boolean.py`,
  `test_with_.py`, `test_bytes.py` and five more), and `import pytest as
  _pytest` in `test_frozen_set.py`.

Moving all of them is mechanical. Each local name was checked against the
module's top-level names and against the other local imports in the same file:
there are no clashes, so every import can move as written. Four use `as`, and
keep their alias.

The two reasons the exemption gives in `pyproject.toml` do not apply:
monkeypatching swaps a module *attribute*, which works the same whichever
scope imported the module, and no test exercises import-time behaviour.

**Fix.** Hoist the 333 to the top of their modules, merging into the imports
already there, and remove `PLC0415` from the `tests/*` per-file ignores so a
new one is refused at commit time. `RUF043` stays exempt; it is unrelated.

Out of scope: the 140 function-local imports left in `poop/` break real cycles,
which `CONTRIBUTING.md` allows, and each one names its cycle. Removing those
would need the type modules reorganised so `meta.py` and `object.py` stop
sitting under everything else, which is a design change rather than a cleanup.

---

### 2. `{}.values()` is hashable, as CPython's `dict_values` is

```
d = {"a": 1}
v = d.values()
{v}.len().print()
# TypeError: cannot use 'dict_values' as a set element (unhashable type: 'dict_values')
v.hash().print()
# dict_values cannot be hashed — a mutable object has no place as a set
#   element or a dict key (unhashable type: 'dict_values')
```

CPython hashes a `dict_values` by identity: `len({v, d.values()})` is `2`, and
`hash(v) == hash(v)`. POOP already agrees on equality: `v == v` is `True` and
`v == d.values()` is `False`, because `DictValues` defines no `__eq__` and
inherits `Object`'s identity. Only the hash is missing.

It is missing on purpose, in the wrong place. `_DictView`, the base of all
three views, declares `__hash__ = None`, and `INFECTIONS.md` repeats it: "All
three views are unhashable". That is true in CPython for `dict_keys` and
`dict_items`, which are set-like and compare by contents, and false for
`dict_values`, which is neither. The same section opens by saying the views
mirror Python's "exactly", and its own table lists `DictValues` equality as
"inherits `Object` identity (Python parity)". Identity equality without the
identity hash is the half that does not mirror.

The refusal's wording is wrong as well. "A mutable object has no place as a
set element" describes a value-compared container. A `dict_values` is compared
by identity, so its contents changing cannot move it in a set.

**Fix.** Move `__hash__ = None` from `_DictView` down to `DictKeys` and
`DictItems`. Each of them already defines `__eq__`, which clears the hash by
itself, and each carries a `# noqa: PLW1641` saying it is unhashable as in
CPython, so the explicit line documents the intent rather than changing it.
`DictValues` then inherits `Object.__hash__`. A test asserts both directions:
a values view is a set element and a dict key, while keys and items views are
still refused. `INFECTIONS.md` changes "All three views are unhashable" to
name the two that are and the one that is not.
