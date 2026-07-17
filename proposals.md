# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Every claim below was verified by running the interpreter; the quoted output is real.

---

## Object leaks

Surfaces that handed a raw Python object — or a POOP-internal identity — to user
code. All four are closed; the decisions are kept here so they are not
re-derived.

### ~~1. POOP class objects render as CPython's `<class '...'>`~~ — DONE

**Decision: mis-diagnosis in part; cloak the four uncloaked classes.** The
`<class 'int'>` rendering is *deliberate* — `test_type_names.py` asserts it and
`INFECTIONS.md` documents it, because `repr(int)` in Python is `<class 'int'>`
and POOP builtins mirror Python. So a class nested in a collection rendering as
`<class 'int'>` is correct, not a leak, and a `PoopMeta.__repr__` returning the
bare name would have broken that mirror.

The genuine leak was only the **module path** on the four classes that never
cloaked: `Block`, `Error`, `Try`, `With` answered `<class 'poop.types.block.Block'>`.
Fixed by patching `__module__`/`__name__` like every other wrapper (`Block` →
`function`, `Try`/`With` keep their names, `Error` via item 2's transparency).
Recorded in `INFECTIONS.md` under *Namespace hygiene*.

### ~~2. `class_name()` leaks the internal wrapper name~~ — DONE

**Decision: mirror Python.** A lambda answers `function` (`type(lambda: 0)` is
`function` in CPython — there is no `lambda` type; `<lambda>` is the instance's
`__name__`, not the class's). A caught `Error` answers the wrapped exception's
name: `class_()` delegates to `kind()`, so `e.class_name()` → `IndexError`,
matching Python's `except IndexError as e` where `type(e)` is `IndexError`.
`kind()` stays as the explicit spelling.

### ~~3. `dir()` leaks a `_poop_*` name and every private internal~~ — DONE

**Decision: hide internals.** `Object.dir()` and `PoopMeta.dir()` now filter
every `_`-prefixed name — dunders and privates, including the mangled
`_poop_own_set` — matching the REPL's `:methods`. POOP diverges from CPython's
exhaustive `dir()` deliberately, honouring "`_poop_*` never reaches user output".
Recorded in `INFECTIONS.md` under *No `dir`*.

### ~~4. `get_attr` returns the raw Python primitive behind any private attribute~~ — DONE

**Decision: reject privates.** `get_attr`/`has_attr`/`set_attr`/`del_attr` (both
instance and class side) now refuse every `_`-prefixed non-dunder name through a
new `_reject_private`, the single-underscore twin of the closed dunder guard —
so `get_attr("_value")` no longer hands back the raw primitive a wrapper holds.
The class-side `has_attr`, which had skipped the guard entirely, now calls it.
Recorded in `INFECTIONS.md` under *No dunder attributes*.

---

## Iterator protocol

### ~~5. Iterators understand only `next` and `do`, not the rest of the iterable protocol~~ — DONE

**Decision: match Python — full protocol (option a).** An iterator *is* an
iterable, so it now answers the same messages as collections and views. Before,
the lazy views (`Map`, `Filter`, `Enumerate`, `Zip`, `Range`) and the eager
collections mixed in `_IterableMixin` while the one-shot iterators from `.iter()`
(`_IteratorBase` subclasses) answered only `next` and `do` — so `"42".iter().map(…)`
and `[1,2,3].iter().filter(…)` were rejected even though Python accepts an
iterator as a `map`/`filter` argument. The tell it was a wiring gap: `_IteratorBase`
hand-duplicated `do()` from the mixin.

Fixed by making `_IteratorBase` inherit `_IterableMixin` and deleting the
duplicated `do`. Every iterator now answers `do`, `map`, `filter`, `filter_false`,
`find`, `reduce`, `sum`, `min`, `max`, `all`, `any`, `enumerate`, `zip`. Consuming
messages drain the one-shot iterator (matching Python); lazy ones return a fresh
view over the remainder. Recorded in `INFECTIONS.md` under *No `iter`*; covered by
`tests/test_types/test_iterator_base.py`.

---

## Hidden boolean semantics

### ~~6. Chained comparisons smuggle the forbidden implicit `and`~~ — DONE

**Decision: accept chains (option b).** A chained comparison (`1 < 2 < 3`) is a
single `ast.Compare` node with multiple comparators that Python evaluates as
`(1 < 2) and (2 < 3)` with short-circuit — an implicit `and` with no `and`
token, which `no_and_or` (inspecting only `ast.BoolOp`) does not catch. Rather
than add a `no_comparison_chain` validator that would reject code no example
relies on, POOP treats `<`/`>`/`==` chaining as plain operator sugar — a single
comparison already keeps its operator (like `+`), and a chain reads as more of
the same. Recorded in `INFECTIONS.md` under *No `and`/`or`* as the one
deliberate place an implicit `and` survives; the explicit spelling remains
`(a < b).and_(lambda: b < c)`.

---

## Free functions

### 7. Nested `def` inside a method escapes the free-function ban — OPEN

**Symptom.** `no_free_functions` reports a `FunctionDef` only when its
`_class_depth == 0`, so a `def` nested inside a method (its direct parent is a
`FunctionDef`, not a `ClassDef`) is accepted and called receiver-less:

```
>>> def helper(x):        # module level → rejected
...     return x
poop: free functions are forbidden — define methods inside a class
>>> class C(Object):      # nested inside a method → accepted
...     def run(self):
...         def a(x):
...             def b(y):
...                 return y
...             return b(x)
...         return a(42)
>>> C().run().print()
42
```

**Why it may be intended (weaker than #5/#6).** Lambdas — receiver-less callables
invoked as `block()` — are POOP's sanctioned block mechanism and are freely
called, so a nested `def` is essentially a *named, multi-statement lambda*. The
validators still recurse into a nested `def`'s body, so `if`/`for`/subscript/etc.
remain rejected there; the only thing gained over a lambda is a name and multiple
statements. So this is a purity gap, not an escape from message-passing rules.

**Decision needed:**

- **(a) Tighten.** Report a `FunctionDef`/`AsyncFunctionDef` whose *direct* parent
  is not a `ClassDef` (Smalltalk has blocks, not named local functions). Forces
  helpers to be lambdas.
- **(b) Accept.** Keep the depth check and document nested `def` as the allowed
  multi-statement analog of a lambda.

All output above was produced by running the interpreter at this commit.

---

## More object leaks

### ~~8. `includes` leaks an internal attribute name on a wrong-type argument~~ — DONE

**Decision: mirror Python.** Several `includes` methods unwrapped their argument
(`arg._value` / `arg._items`) *before* any type check, so a POOP argument lacking
that attribute (a `List`/`Set`/`Dict`/`Tuple` has no `_value`; a non-`Tuple` has
no meaningful `_items`) routed through dispatch and leaked the internal name —
e.g. `list does not understand #_value`. Found by testing membership with a
mismatched argument type:

```
>>> {1:2}.items().includes(1)     # int has no _items
poop: MessageNotUnderstood: int does not understand #_items ...
>>> range(5).includes([1,2])      # list has no _value
poop: MessageNotUnderstood: list does not understand #_value ...
>>> b"abc".includes([1,2])        # list has no _value
poop: MessageNotUnderstood: list does not understand #_value ...
>>> "abc".includes([1,2])         # list has no _value
poop: MessageNotUnderstood: list does not understand #_value ...
```

Fixes, each restoring faithful Python semantics with no leak:

- **`DictItems.includes`** — delegate to `__contains__` (already guarded with
  `isinstance(item, Tuple)`): `return to_boolean(pair in self)`. A non-pair
  answers false, like `1 in {1: 2}.items()`. Also removes duplicated arity logic.
- **`Bytes`/`ByteArray`/`Str.includes`** — use the codebase's faithful-unwrap
  idiom (as in `bytes.join`): `getattr(arg, "_value", arg)`. A `_value`-bearing
  argument keeps its subsequence/substring semantics
  (`b"abc".includes(b"ab")` → true); a non-`_value` argument reaches
  `bytes`/`str`'s `__contains__` raw and raises the faithful `TypeError`
  (`a bytes-like object is required, not 'list'` /
  `requires string as left operand, not list`).
- **`Range.includes`** — same `getattr` unwrap; a non-`_value` argument reaches
  `range.__contains__` raw and answers false by equality scan, like
  `[1,2] in range(5)`.

`DictKeys.includes`/`DictValues.includes` were already correct (they delegate to
Python `in` on the raw data). Covered by new `test_includes_*` regression tests in
`test_dict_items.py`, `test_bytes.py`, `test_byte_array.py`, `test_str.py`,
`test_range.py`.

### ~~9. Same `_value` leak across the wider `Str`/`Bytes`/`Range`/numeric method surface~~ — DONE

**Decision: mirror Python — faithful unwrap everywhere.** Item 8's fix was
generalised into a named idiom, `_faithful(arg)` in `poop/types/_unwrap.py`
(a thin `getattr(arg, "_value", arg)` returning `Any`), and `_unwrap`'s
optional-argument path was made faithful the same way. Every method that
unwrapped a *mandatory* argument inline as `arg._value` now routes through
`_faithful`, so a foreign argument (a `List`/`Set`/`Dict`/`Tuple` with no
`_value`) reaches the underlying Python call raw and raises the faithful
`TypeError` — `count() argument 1 must be str, not list` — instead of leaking
`list does not understand #_value`.

Swept: `count`, `find`, `index`, `rfind`, `rindex`, `replace`, `removeprefix`,
`removesuffix`, `partition`/`rpartition`, `center`/`ljust`/`rjust`, `zfill`,
`startswith`/`endswith`, `hex`, `fromhex`, and the `_unwrap`-mediated
`strip`/`lstrip`/`rstrip`, `split`/`rsplit`, `start`/`end` bounds across `Str`,
`Bytes`, `ByteArray`; the `ByteArray` container mutators too (`append`,
`extend`, `insert`, `remove`, `pop`, `at`, `at_put`, and indexing); `count` /
`index` / `at` on `Range`; and `Int.to_bytes`/`from_bytes`, three-argument
`Int.pow` (modulus), `Int`/`Float.round`, `Float.fromhex`. Audited and left
untouched: `Int`/`Float`/`Complex` arithmetic and comparison already route a
foreign operand to `NotImplemented` (via `_num_value`/`_integral_value`/
`_coerce`), so CPython raises the faithful `TypeError` and no `_value` leaks.

Covered by new `*_wrong_type_arg_is_faithful_not_value_leak` regression tests in
`test_str.py`, `test_bytes.py`, `test_byte_array.py`, `test_int.py`,
`test_float.py`, and `test_range_wrong_type_args_are_faithful_not_value_leaks`.
Recorded in `INFECTIONS.md` under *No dunder attributes* (the faithful-unwrap
idiom).
