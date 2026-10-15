# Proposal

## Why

The same review of `poop/transformers/` and `poop/validators/` found
bindings nothing emits, factories that wrap a constructor that already has
the shape, a dead branch, two helpers with one name and one job, and two
validators that reimplement a shape the three shared validator helpers
already give. None of it changes what a program observes.

## What Changes

- **Seven bindings go from `BINDINGS`**: `_poop_boolean`, `_poop_bytearray`,
  `_poop_memoryview`, `_poop_frozenset`, `_poop_frozendict`, `_poop_sentinel`
  and `_poop_dict`. No rewrite emits them (each class is reached through its
  `_cls` alias), nothing in `poop/` or `tests/` reads them, and the REPL
  completer hides `_poop_*` names. `_poop_complex` was on the first list and
  stays: it becomes the literal target below, as `_poop_int` is for `int`;
  `_poop_frozendict`, found by the namespace test, takes its place.
- **`make_constructor` is deleted** from `_collection.py`; `_poop_list`,
  `_poop_tuple` and `_poop_set` bind the class, whose `__init__` is already
  variadic. **`_poop_complex_literal` is deleted**; `literal_target` points at
  the class binding as `int`, `float`, `str` and `bytes` do.
- **The `Range` branch in `make_iterable_from` is deleted**: `Range` defines
  `__iter__`, so the `Iterable` branch below it answers the same.
- **One `rebind(target, helper)`** in `base.py` beside `name_at`/`call_at`
  replaces the two private `_rebind`s of `varargs.py` and `unpack.py`.
- **`unpack.py`'s target guard** lists `ast.Name` and `ast.Attribute` only,
  matching the comment above it.
- **`range.py` normalises its one, two or three arguments once** and builds
  one `Range`, instead of three branches each re-deriving the inclusive stop.
- **A fourth shared validator helper, `ShadowValidator`** (`_shadow.py`),
  holds the `protected` frozenset + `{name}` message + visitor shape that
  `no_builtin_shadow` and `no_namespace_shadow` each write, so each becomes
  two class attributes like a `CallNameValidator` subclass.
- **Smaller alignments**: `_is_super_call` in `no_dunder_attribute.py` and
  the `isinstance(node.func, ast.Name) and …` tests in `base.py` and
  `dict.py` become `match` class patterns; the converters that spell a
  refused type as `type(x).__name__` use `__qualname__` like their siblings;
  the dead `if node.body` guard in `return_.py` goes.

Out of scope, and why: the `slice` fold and the `dict(**x)` fold, which do
change behavior and are in `fix-behaviour-leaks`; `_EllipsisRewriter`'s own
`visit_Name`, where subclassing `BuiltinRewriter` would cost a
`visit_Constant` override and save nothing; `ClassTransformer` binding
`_poop_object` while `ObjectTransformer` emits it, which the duplicate-key
guard forces.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — source-level refactor; `skip_specs: true`)

## Impact

- `poop/transformers/`: `boolean.py`, `complex.py`, `byte_array.py`,
  `memory_view.py`, `frozen_set.py`, `sentinel.py`, `dict.py`,
  `_collection.py`, `list.py`, `tuple.py`, `set.py`, `base.py`,
  `varargs.py`, `unpack.py`, `range.py`, `int.py`, `float.py`, `return_.py`.
- `poop/validators/`: new `_shadow.py`; `no_builtin_shadow.py`,
  `no_namespace_shadow.py`, `no_dunder_attribute.py`.
- Tests: `tests/test_types/test_complex.py` imports
  `_poop_complex_literal`; `tests/test_transformers/test_namespace.py` may
  enumerate bindings; the two shadow validator suites.
- Docs: `CONTRIBUTING.md`'s validator section names the three shared helpers
  and gains the fourth; `README.md` counts are unchanged.
