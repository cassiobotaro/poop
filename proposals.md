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

