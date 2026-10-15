# Design

## Context

See proposal.md - Why. The constraints the refactor works under:

- A wrong-arity call to a message is reported by CPython from the
  *function's* `__qualname__`, which `cloak` sets to `<cloaked class>.<name>`
  for the functions a class owns. A body moved onto a mixin cloaked as
  `object` therefore reports `object.<name>()`. The pattern `_sequence.py`
  documents keeps a one-line `def` on each concrete class and shares only a
  private helper.
- `_Mixin.__init_subclass__` cloaks a mixin and turns its public methods
  into `message` descriptors; a mixin outside it (`_SetAlgebraMixin` today)
  gets neither.
- `Dict._wrapping(data)` and `FrozenDict._wrapping(data)` build an instance
  over a raw dict without copying; `Dict.at_put` is a plain assignment.
- `_num_value` already folds `Boolean` and `Int` to a native `int`.

## Goals / Non-Goals

**Goals:**
- Every duplicated body named in the proposal exists once.
- No message changes its answer, its refusal sentence or the qualname its
  arity sentence names.

**Non-Goals:**
- Any behavior change (`fix-behaviour-leaks` holds those).
- Hoisting the `includes`/`len` one-liners (see proposal, out of scope).

## Decisions

- **`_mapping_data` lives in `mapping_proxy.py`**, which already lazily
  imports `_MappingMixin`, and every caller already imports `MappingProxy`
  eagerly, so no new edge and no new `lazy from`.
- **Set algebra helpers take the CPython method name** (`"union"`,
  `"issubset"`) and reach it with `getattr(self._data, name)`: one helper per
  shape (answers a set / answers a Boolean) rather than one per message.
  Alternative considered: `operator.methodcaller`, which reads no clearer
  for a variadic call.
- **`answered` is a function, not a decorator**: the five sites differ in
  which dunder they call and which selector they name, and a function call
  reads at the site; a decorator would hide the selector.
- **`indexing` is a `contextlib.contextmanager`** so the `raise … from None`
  inside the generator propagates from `__exit__` exactly as the inline
  `except` clauses do today; `at_index` and the two `at_put`s become a
  `with` block around one statement.
- **`_own_entry(cls, name)` answers `(klass, entry)` or `None`** so
  `_reflected` can still bind through the owning class and `_instance_only`
  can still stop at the first class that defines the name.
- **`_SetAlgebraMixin(_Mixin)`**: verified that the MRO of `Set`,
  `FrozenSet`, `DictKeys`, `DictItems` stays consistent and the four suites
  pass; the only visible difference is `_SetAlgebraMixin.__name__` becoming
  `object`, which only an interpreter internal can read.

## Risks / Trade-offs

- [A helper hoisted onto a mixin changes an arity sentence] → every hoist
  keeps the public `def` on the concrete class; the wording sweep
  `tests/test_no_python_wording.py` and the arity tests pin the qualnames.
- [`Range.__init__` reordering changes which refusal fires first for a bad
  start and a zero step] → the order "bounds, then step" is kept, and
  `tests/test_types/test_range.py` is run as the check.
