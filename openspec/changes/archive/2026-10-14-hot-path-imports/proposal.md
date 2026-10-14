# Proposal

## Why

`poop/types` carries 277 function-local imports, written to break import
cycles between the hubs (`object`, `meta`, `boolean`, `int`, `float`,
`string`, `block`). Each costs about 215 ns on Python 3.15 against ~20 ns
for a module-level name, and a handful sit on the paths every program runs
through. Counting the imports that fire while the 43 example programs run
(6294 in all) ranks them: `Object.__getattribute__` imports `_MethodBlock`
on every message sent to an object (1809 fires), `Int._arith` imports
`Float` on every `+ - * / // %` (887), `_num_value` runs three imports on
every ordering or equality between numbers (555 each), `Object.print` two
per call (391), the numeric `__eq__` two more (381), `_order` one (174),
`Object.repr` one (70), `PoopMeta.__eq__` two (40). Everything else fires
fewer than fifteen times across all examples. Micro-timed today, `Int < Int`
takes ~3700 ns and `Int == Int` ~4200 ns, of which the imports are roughly
a third; a message send such as `(5).abs()` ~3800 ns.

An earlier proposal to hoist the imports to module level was rightly closed:
the hubs are needed while the classes are being defined, so the cycles are
real. The imports do not have to run on every call to break them, though.

## What Changes

- **`_num_value` stops importing.** `Int`, `Float` and `Boolean` already
  share `_NumericCompareMixin` and already supply `_order_value()`; the
  coercion becomes one `isinstance` on the mixin and one hook call, no
  imports, no rung list to keep in order.
- **The numeric `__eq__` asks the mixin first.** The `Complex` import moves
  to the miss path, so `Int == Int` never runs it; `Int == Complex` still
  does, and still answers as CPython does.
- **A late-binding helper** in `poop/types/_late.py`: `late(module, name)`
  answers a zero-argument getter cached with `functools.cache`, so a hot
  site pays the import once per process and a C-level cache hit (~50 ns)
  afterwards. Used at the measured hot sites only: `Object.__getattribute__`
  (`_MethodBlock`), `Object.print` / `repr` / `ascii`, `PoopMeta.__eq__`,
  `_NumericCompareMixin._order` / `__eq__` (`to_boolean`, `false`),
  `Int._arith` / `__pow__` (`Float`, `to_poop`), `Boolean._as_int` (`Int`),
  `_iterable_mixin.map` / `filter`, and the `_argument` guards that import
  `_is_absent` / `_searched` on every call.
- **A guard that the hot paths stay import-free**: a test that counts
  `poop/`-internal imports while the hot operations run and asserts zero.
  Timing is not asserted in tests (CI timing is noise); the before/after
  measurement is recorded in `design.md` as part of the change.
- **`INFECTIONS.md`**: one paragraph recording the rule — a cycle is broken
  by a function-local import, and a *hot* site binds late instead — with the
  measurement that drew the line.

No observable behavior changes: every message answers what it answered, in
the same words; the test suite is the proof, and `skip_specs` is declared.

Out of scope, and why: the ~260 cold sites (fewer than fifteen fires across
every example; rewriting them buys nothing measurable and touches 40 files);
the duplication between `PoopMeta` and `Object`, explored and kept on
purpose (class attribute lookup searches the class MRO before the
metaclass); any change to what `_MethodBlock` wraps or when.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — performance-only refactor with no behavior change; `skip_specs: true`)

## Impact

- `poop/types/_late.py` (new), `_numeric_compare.py`, `object.py`,
  `meta.py`, `int.py`, `boolean.py`, `_iterable_mixin.py`, `_argument.py`.
- Tests: `tests/test_late.py` (new), `tests/test_hot_paths_bind_late.py`
  (new, the import counter).
- Docs: `INFECTIONS.md` (one paragraph). `README.md` counts are unchanged.
