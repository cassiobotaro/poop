# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

---

### ~~1. `mro()` and `register()` reach every POOP class from the metaclass~~ — DONE

**Decision + implemented.** `PoopMeta` inherited two public names from `ABCMeta`:
`type.mro`, which answered a raw Python list of raw classes — `__mro__` under a
spelling `no_dunder_attribute` cannot see, holding the Python `object` that
`superclass` stops short of on purpose — and `ABCMeta.register`, which made
`is_instance` answer true for a class that never inherited from the receiver.
Neither was listed by `dir()`, so both were undiscoverable *and* reachable.

Both are now `class_side` refusals naming `superclass` and `is_subclass`, via a
new `_refuse_native` (the twin of `_refuse`, whose "asks an instance about its
class" wording said nothing true about them). `mro` cannot refuse
unconditionally: CPython calls the metaclass's `mro` to *compute* a new class's
MRO, so an outright ban breaks every `class` statement — verified, it raises at
class-creation time. The class has no `__mro__` during that call and does
afterwards, which is the line the guard draws between the interpreter asking and
a program asking. `poop/types/meta.py`, `tests/test_types/test_meta.py`,
`INFECTIONS.md`.

---

### ~~2. `With` enters the context manager before checking `__exit__`~~ — DONE

**Decision + implemented.** `With.do` called `cm.__enter__()` unguarded and
reached for `__exit__` only after the body ran, so a manager that could be
entered but never exited ran its acquisition and then failed — the side effect
happened with nothing left to undo it.

A new `_protocol(cm)` resolves both slots up front, as Python's `with` does, and
looks them up on the *type*, so a `does_not_understand` hook answering a
callable cannot forge a context manager. The refusal names the missing half of
the protocol (`int does not support the context manager protocol — it cannot be
entered`) rather than the dunder CPython names: the wording first written for
this fix spelled `__exit__`, which `tests/test_no_python_wording.py` forbids as
naming a banned construct, so both failing programs were added to that sweep.
`poop/types/with_.py`, `tests/test_types/test_with_.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~3. `Int.max` / `Int.min` / `Float.max` / `Float.min` drop the `key` argument~~ — DONE

**Decision + implemented.** All four now take `key` as a keyword-only argument
and route through the shared `_minmax`, so `(5).max(3, key=…)` answers what
`max(5, 3, key=…)` does. Keyword-only because positionally a block is
indistinguishable from one more operand — which is exactly how it was being
read, so a *comparable* extra argument would have answered a plausible wrong
number in silence. `default` stays refused on the scalar form, as CPython
refuses it too.

One structural change fell out: `_minmax` and `_MISSING` lived in
`_iterable_mixin`, which imports `Int`, so the scalar rungs could not reach them
from the top of the file. They moved to a new `poop/types/_minmax.py` with no
POOP imports at all; `_iterable_mixin`, `Str` and `Dict` import from there now.
`poop/types/int.py`, `poop/types/float.py`, `poop/types/_minmax.py`,
`poop/types/_iterable_mixin.py`, `tests/test_types/test_int.py`,
`tests/test_types/test_float.py`, `INFECTIONS.md`.

---

### ~~4. `Range` publishes its internal inclusive bound through `stop()` and `print()`~~ — DONE

**Decision + implemented.** The inclusive upper bound is an encoding, not a
language feature — `__eq__` already called it that — and `stop()` and `__str__`
read the raw slot, so `range(3).stop()` answered `2` and `range(3)` printed as
`range(0, 2)`, a spelling that reads back as a different sequence. `Slice`,
handed its bound rather than encoding one, had always answered the exclusive
form, so a single selector meant two things depending on the receiver.

Both now report through `_range()`, the one place the encoding is undone:
`range(3).stop()` is `3`, and `range(3)`, `range(1, 10, 3)`, `range(0, 4, 2)`,
the reversed forms and the empty range all print exactly as CPython prints them.
`start()` and `step()` still read the slots — neither is re-encoded. Four
existing tests pinned the old spelling and were updated: they built `Range`
directly with the internal bound, so only the *answers* changed.
`poop/types/range.py`, `tests/test_types/test_range.py`, `INFECTIONS.md`.

---

### ~~5. A caught `Error` calls itself `object` when it refuses a message~~ — DONE

**Decision + implemented.** `Error.does_not_understand` now passes the wrapped
exception's name to `explain` through a new optional `label` parameter, so
`e.zzz()` reports `ZeroDivisionError does not understand #zzz` — the name the
same `e` already answered from `class_()`, `class_name()` and `__str__`. All
three hint shapes (Smalltalk selector, typo, `:methods`) are unchanged.

The label is passed rather than derived: asking each receiver for its class
would route through a message a proxy is free to answer with anything, and
`type(obj).__name__` stays correct for every other receiver.
`poop/types/error.py`, `poop/types/_selectors.py`,
`tests/test_types/test_error.py`, `INFECTIONS.md`.

---

### ~~6. Plain attribute access still answers a raw bound method~~ — WON'T FIX

**Decision: accepted leak, measured.** `[1, 2].len` answers CPython's bound
method while `get_attr("len")` answers a `Block`, so the two spellings of "hand
me this method" disagree. The proposal named `__getattribute__` as the only hook
that sees a successful lookup, and asked for a measurement before committing to
it. The measurement was taken, on the obvious implementation (wrap through
`_as_block`, skipping `_`-prefixed names — without that guard `Block.__call__`
re-wraps its own `_fn` and recurses without bound):

| | 200k message sends |
|---|---|
| today | 1.12 s |
| with `Object.__getattribute__` | 2.02 s |

**+81% on every message send in the language**, to close a leak in a spelling
that has no idiomatic use — POOP has no free functions to pass a method to. The
same probe also broke 9 tests outright, all of them wrong-arity diagnostics that
began blaming the `Block` wrapper instead of the receiver, so the cost is not
only throughput: it would undo the `cloak` work that makes those messages read
in POOP's vocabulary.

The validator route stays unimplementable for the reason the proposal gave: an
`ast.Attribute` in `Load` position cannot be told apart from a state read
without runtime types, and `self.count` is a plausible field name that is also a
message. Recorded in `INFECTIONS.md` beside the `get_attr` entry so the next
reader finds the decision rather than rediscovering the leak.

---

### ~~7. A container that holds itself exhausts the stack instead of printing~~ — DONE

**Decision + implemented.** `List`, `Tuple` and `Dict` build their displayed
form from `repr` of each element, so a container reachable from itself recursed
until CPython gave up: `xs = [1]`, `xs.append(xs)`, `xs.print()` answered
`RecursionError: maximum recursion depth exceeded` — a report about POOP's own
internals, raised by a program that only asked to see its data. `Dict` (a value
holding its own dict) and `Tuple` (immutable, but free to hold a list that holds
the tuple) failed the same way.

All three now carry `reprlib.recursive_repr` with the fill value CPython uses
for that container, so `[1, [...]]`, `([(...)],)` and `{'a': {...}}` come back
character-for-character as Python prints them — including through `List.print`,
which formats each element with `str` and so reaches the guarded `__str__` one
level down. `Set` and `FrozenSet` are left alone on purpose: a cycle through a
set would have to hold something unhashable. `poop/types/list.py`,
`poop/types/tuple.py`, `poop/types/dict.py`, `tests/test_types/test_list.py`,
`tests/test_types/test_tuple.py`, `tests/test_types/test_dict.py`,
`INFECTIONS.md`.

---

### ~~8. `key=None` is read as a comparison block by every message that takes one~~ — DONE

**Decision + implemented.** `_sorted` and `_minmax` tested `if key is not None`.
POOP's `None` is a `NoneClass` instance, not Python's `None`, so the language's
own null passed the test and reached CPython as the comparison function:
`xs.sorted(key=None)`, `xs.sort(key=None)`, `col.min(None)`, `col.max(None)`,
`(5).max(3, key=None)` and the `Str`/`Dict` rungs all answered `'NoneType'
object is not callable` — CPython's default spelling for the argument, refused
by the substitute for the builtin that documents it.

Both helpers now use `_is_absent`, the test every other optional argument in the
language already used (`_unwrap` says so in as many words: "user code that
passes `none` is handled identically to the missing-arg case"). `_minmax` keeps
its rule of importing no POOP module at runtime — `int.py` imports it, and
`_unwrap` reaches `object.py` — so the import is function-local and the
`NoneClass` in its signature is `TYPE_CHECKING`-only. The `key` annotations
widened to `… | NoneClass | None` across `_iterable_mixin`, `Int`, `Float`,
`Str`, `Dict`, `List` and `Tuple`, since accepting the value is now the
contract. `poop/types/_minmax.py`, `poop/types/_iterable_mixin.py`, and the six
wrappers; `tests/test_types/test_list.py`, `test_tuple.py`, `test_dict.py`,
`test_int.py`, `INFECTIONS.md`.

---

### ~~9. `sorted` and `sort` take `key` positionally, which `min`/`max` already refused~~ — DONE

**Decision + implemented.** `List.sorted`, `List.sort` and `Tuple.sorted`
declared `key` and `reverse` as ordinary positional parameters. CPython spells
both `(*, key, reverse)`, and proposal 3 settled the reason for `min`/`max`
three items ago: positionally a block is indistinguishable from one more value,
so `xs.sorted(f)` and `xs.sorted(reverse_flag)` read identically to the
receiver, and `xs.sorted(None, True)` — the plain reading of "sort descending" —
handed `None` to the key slot.

All three are keyword-only now, which is also what the "a substitute mirrors the
builtin's full Python signature" rule asks for. Nothing in `examples/` or the
suite passed either argument positionally, so the only callers to update were
the two new refusal tests. `poop/types/list.py`, `poop/types/tuple.py`,
`tests/test_types/test_list.py`, `tests/test_types/test_tuple.py`,
`INFECTIONS.md`.

---

### ~~10. Slicing a `Range` materializes it into a `List`~~ — DONE

**Decision + implemented.** `Range.slice` answered `List(*(Int(i) for i in
self._range()[py]))`. The native slice is O(1), but wrapping its members is not:
`range(1000000000000).slice(0, 3)` — three elements in CPython — allocated an
`Int` per member of the whole selected sequence, and `range(2000000).slice(None,
None, 2)` took 1.27s against Python's 0.00s. The type was wrong too:
`range(10)[1:3]` is `range(1, 3)` in Python, and `Range.reversed()` sitting
directly below already answered a `Range`, so one receiver returned a lazy range
from one slicing message and an eager list from the other.

`slice` now re-encodes the native slice as a `Range`, shifting the exclusive
stop back by `sign` exactly as `reversed()` does. Verified against CPython for
the forward, stepped, negative-step, negative-index, empty and empty-receiver
forms. Three tests pinned the `List` answer and now pin the `Range` plus its
materialized elements. `poop/types/range.py`, `tests/test_types/test_range.py`,
`tests/test_types/test_slice.py`, `INFECTIONS.md`.

---

_No open proposals — every item above is closed. Closed items live in the git history._
