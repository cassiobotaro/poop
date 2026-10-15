# Design

## Context

See proposal.md — Why. Constraints that shape the fixes:

- `_ValueEqMixin.__eq__` tests `isinstance(other, type(self))`; CPython
  calls the right operand's `__eq__` first when it is a subclass of the
  left's class, so the subclass's test always runs with the base on the
  other side and answers `false`, which is not `NotImplemented`.
- `Error` is `@final`, cloaked as `object`, and forwards nothing but its
  three messages; its `does_not_understand` composes the refusal.
  `_PYTHON_ATTRIBUTES` lists the five `BaseException` names and the
  sentence each gets.
- `Range` has `len` but no `__len__`, so `Object.__bool__` answers `True`;
  `includes` is inherited from the iterable mixin and walks the range.
- `_TrueClass` and `_FalseClass` are two `@final` subclasses of `Boolean`;
  `class_()` answers `type(self)`.
- `an_int(value, selector, role)` words `#<selector>'s <role> must be an
  int, got <article>`; `text_like` words the str family; `indexing` words
  the two index failures; `no_element_equal_to` words a miss;
  `_searched` folds a `Boolean` needle to its int for a raw-int container.
- Constructors word their arity through the converter; `Try` and `With` are
  classes bound directly in `DEFAULT_NAMESPACE`, so CPython words theirs.

## Goals / Non-Goals

**Goals:**
- Every scenario in the delta specs passes; no existing example changes its
  output.
- Every new sentence is composed by a helper that already exists
  (`an_int`, `text_like`, `no_element_equal_to`, `indexing`), so the
  vocabulary does not grow.

**Non-Goals:**
- Unifying the three index-refusal phrasings (`an_int`, `indexing`,
  `_resolve_py_slice`) into one — a vocabulary decision for a change of
  its own; here each site uses the helper its siblings use.

## Decisions

- **Symmetric comparability**: `_eq_comparable` answers `True` when either
  operand is an instance of the other's class, then falls through to the
  group test. Hash is already by value on every class that defines
  `_eq_attr`. Alternative: compare against the class that *declares*
  `_eq_attr` (walk the MRO) — correct too, but a longer read for the same
  answer.
- **`Error` forwards instance state, never class attributes**: in
  `does_not_understand`, before refusing, read `vars(self._exception)`
  (the native's `__dict__`, which only a program's subclass fills) for a
  public name and answer it; `has_attr`, `get_attr` and `dir` read the same
  dict. Methods live on the class and dunders are filtered by `is_message`,
  so neither is reachable through this path.
- **`Error.__eq__`/`__hash__` by the wrapped exception's identity**, the
  shape `_MethodBlock._identity` uses for bound methods.
- **`Range.__len__` and `__contains__`**: `__len__` is what the rest of the
  family does for truthiness; `__contains__` delegates to the native range so
  `includes` stops walking. `includes` keeps going through `_searched` for
  the `Boolean` needle.
- **`Boolean.class_` answers `Boolean`** (the class cloaked as `bool`),
  overriding `Object.class_` on the base so both singletons inherit it;
  `is_instance`, `is_subclass` and `type(true)` in tests are untouched.
- **`a_boolean` joins `_argument.py`**: `#xor expects a bool, got an int`,
  the `a_block` sentence shape. Folding through truthiness was considered
  and rejected: `False.xor(5)` reading as `False.xor(True)` would silently
  accept the mistake `and_`/`or_` refuse.
- **`class_side.__delete__`** raises the `__set__` sentence; `PoopMeta.
  del_attr` wraps `delattr` as `Object.del_attr` does. `PoopMeta.format` and
  `print` route through `text_like` and `_template_refusal` as the instance
  side does. `Object.print` and `_print_items` take an `_opt_text` variant
  that admits `MISSING`/`none` and otherwise calls `text_like`.
- **`Try`/`With` take `*args`** and count them before `_require_block`, so
  the arity sentence is composed in POOP's words with `nothing` / `N
  arguments`, matching the converters' phrasing.
- **Data-type sites**: `memory_view.py` swaps `_faithful` for `_searched`
  in three messages; `ByteArray.at_put` guards the value with `an_int`
  before `indexing`; `_poop_range` guards each argument with `an_int`
  (roles `start`/`stop`/`step`) before the zero-step check; `_search` in
  `string.py` and `_bytes_like.py` catches `ValueError` for `index`/`rindex`
  and raises `no_element_equal_to`; `Int.__pow__` accepts `(Int, Boolean)`;
  `FrozenDict.hash` catches the `TypeError` and words it with the value's
  kind; `Slice.indices` resolves its bounds through the same check
  `_resolve_py_slice` runs.
- **`no_private_attribute`'s sentence** names `self`/`cls` and "send a
  message"; the module docstring's worked example is rewritten to match.

## Risks / Trade-offs

- [Symmetric equality makes `Name("a")` and `Name2("a")`, two unrelated
  subclasses of `str`, equal] → CPython agrees (`str.__eq__` compares
  values); the group test already made `set == frozenset` True by value.
- [Forwarding exception state exposes `self._x` stored by a program's
  `__init__`] → only public names are answered; `is_message` filters the
  rest, as `dir` does everywhere.
- [`range`'s converter now refuses what CPython words differently; two
  tests pin the old sentence] → they change in the same commit; the
  transformer docstring that justified keeping CPython's sentence is
  rewritten to cite `an_int`.
- [The wording sweep skips `print`] → the sweep redirects stdout for
  `print` instead of skipping it, so the new sentence is pinned.
