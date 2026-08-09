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

### ~~11. The `at` treatment never reached the messages that *remove* an element~~ — DONE

**Decision + implemented.** `_at.py` reworded `at`, `List.pop`, `List.index`
and `List.remove`; the six messages that remove an element from a `Dict`, a
`Set` or a `ByteArray` failed exactly the way its docstring quotes — `KeyError:
'b'`, a bare repr with no sentence, and `popitem(): dictionary is empty`, a
method spelt as a call naming a `dict` by a word POOP does not use.

`no_key` and `nothing_to_remove` join `no_element_at` / `no_element_equal_to`;
`at_key` composes through the first and `List.pop`'s inline sentence through
the second, so neither can drift. Both take the mirror class as an argument:
the sentence is receiver-independent and the class is not — `set.remove` raises
`KeyError` where `list.remove` raises `ValueError`, and a handler naming the one
CPython names must keep matching. `Dict.pop(key, default)` and `Set.discard`
were left alone, as the proposal asked. `poop/types/_at.py`, `dict.py`,
`set.py`, `byte_array.py`, `list.py`, three test modules,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~12. Python's *call* syntax survives inside `min` / `max` / `zip` diagnostics~~ — DONE

**Decision + implemented.** `_minmax` takes the message name (`#min` / `#max`)
and refuses the empty case itself. It passes `_MISSING` *as* the default and
tests the answer's identity rather than catching CPython's `ValueError` — the
proposed `except ValueError` would have caught one raised by the user's own
`key` block and reported it as an emptiness it says nothing about.

`Zip._gen` pairs the sources by hand when `strict` is asked for, so the ordinal
is POOP's rather than read back out of CPython's sentence. It counts
*collections*, not call arguments as the proposal suggested: `zip(a, b)` is a
valid spelling too, so "the 1st argument … the receiver" is true of only one of
the two forms, while `collection 2 ran out while collection 1 still had
elements` is true of both. `poop/types/_minmax.py`, `zip.py`, the five callers,
`tests/test_types/test_iterable_min_max.py`, `test_zip.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~13. `key` and `default` are still positional on every collection `min` / `max`~~ — DONE

**Decision + implemented.** Both are keyword-only on `_IterableMixin.min`/`max`,
`Dict.min`/`max` and `Str.min`/`max`, mirroring CPython's `min(iterable, *, key,
default)` and settling the reading of `xs.min(0)`, which handed `0` to the key
slot: `[1, 2].min(0)` answered `'int' object is not callable` and
`[[3], [1]].min([9])` answered a plausible wrong list without raising at all.
The suite's four positional call sites became the refusal tests.
`poop/types/_iterable_mixin.py`, `dict.py`, `string.py`,
`tests/test_types/test_iterable_min_max.py`, `test_dict.py`, `INFECTIONS.md`.

---

### ~~14. `List.index` silently ignores `stop` when `start` is absent~~ — DONE

**Decision + implemented.** The branching is gone: both bounds pass straight
through, with `len(self._items)` as the missing-`stop` default because
`list.index` — unlike `str.index` — takes no `None` bound. `[1, 2, 3].index(3,
stop=1)` refuses where it used to answer `2`, and an explicit `none` stop no
longer means *stop at 0*.

`Tuple.index` carried the identical branching, which the proposal listed among
the wrappers that "do not have the bug" — it does, and is fixed here too.
`poop/types/list.py`, `tuple.py`, `tests/test_types/test_list.py`,
`test_tuple.py`, `INFECTIONS.md` (whose signature table said `stop` is only
meaningful with `start`, documenting the bug).

---

### ~~15. `reversed` answers a different kind for `Str`, and does not exist for `Bytes`~~ — DONE

**Decision + implemented, in the two commits the proposal asked for.**
`"abc".reversed()` is `"cba"`, so the one message on that receiver that changed
the type composes with the rest of the string protocol again; `list(s.reversed())`
is the spelling for the characters. Then `Bytes` → `Bytes`, `ByteArray` →
`ByteArray` (beside the in-place `reverse`, whose near-miss hint used to offer
itself as the substitute for a copy), `MemoryView` → `MemoryView` through the
native `[::-1]` view, which copies nothing, and `Dict` →
`DictReverseKeyIterator`, one line delegating to `self.keys().reversed()`.
`poop/types/string.py`, `bytes.py`, `byte_array.py`, `memory_view.py`,
`dict.py`, five test modules, `INFECTIONS.md`.

---

### ~~16. `MemoryView` prints the raw memory address~~ — DONE

**Decision + implemented.** `<memoryview of 2 bytes>` replaces `<memory at
0x…>` — the pointer `Object.__hash__` refuses to answer, under a class name
that is neither the POOP name nor the cloak, unstable enough that no test could
pin it. The summary comes with the three messages that make a view readable,
each a ban whose substitute did not exist here: `hex()`, `slice(...)` and
`includes(x)`. `poop/types/memory_view.py`,
`tests/test_types/test_memory_view.py`, `INFECTIONS.md`.

---

### ~~17. REPL tab-completion advertises the internals every other surface hides~~ — DONE

**Decision + implemented.** `is_message` lives beside the hint machinery in
`_selectors.py` and is the single copy of the rule, used by `Object.dir`,
`Repl._meta_methods`, `explain`'s near-miss list and both completer paths.
Tab on `x._` offers nothing now. The completer also reads candidate attributes
off the *type*, so pressing Tab can no longer run a `property` getter — that is,
execute program code. `poop/types/_selectors.py`, `object.py`, `poop/repl.py`,
`tests/test_repl.py`, `INFECTIONS.md`.

---

### ~~18. `Range.index` still answers the sentence `_at.py` was written to delete~~ — DONE

**Decision + implemented.** Three lines, exactly as proposed: `Range.index`
routes through `no_element_equal_to` with `self` as the receiver, so the name in
the message is the one the reader wrote. The program is in the wording sweep.
`poop/types/range.py`, `tests/test_types/test_range.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~19. `Try` and `With` report a non-block argument in Python's calling vocabulary~~ — DONE

**Decision + implemented.** `_require_block` sits in `block.py`, beside the
`Block.__call__` rewording that established the rule, and names the argument
plus the spelling that works: `the manager argument must be a block, got a C —
write With(lambda: …)`. Checked in `__init__` rather than in `run`/`do`, so the
failure lands where the mistake was written.

One thing fell out: with construction guaranteeing a callable, `Try._execute`'s
`if block is not None` guard became unreachable and went, along with the test
that pinned `Try(None)`. `poop/types/block.py`, `try_.py`, `with_.py`,
`tests/test_types/test_try_.py`, `test_with_.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~20. Three slot-less mixins give 36 of 49 wrappers a `__dict__` they declared away~~ — DONE

**Decision + implemented.** `__slots__ = ()` on `_ValueEqMixin`,
`_IterableMixin` and `_SetAlgebraMixin`. Re-measured on the built change: a
`Str` drops from 56 to 40 bytes (an `Int`'s size) and 100 000 of them from
14.2 MB to 9.4 MB. `Object.set_attr` catches the refusal this exposes and
answers `str is a value — it holds no state of its own; only an object of a
class you defined can be given one`, where CPython named `__dict__`.

`tests/test_slots.py` sweeps every class's whole **MRO**, not `vars(cls)`: the
`__dict__` descriptor is installed on the first slot-less base, so a per-class
check would have passed with the bug in place. Verified against the old state —
it fails on exactly the 36 classes the proposal predicted.

One number in the heading is wrong and stays there as written: the sweep counts
**50** POOP classes, not 49, at this commit and at the one that opened the item.
36 of them carried a `__dict__`, which is the figure that mattered and is exact.
`poop/types/_value_eq.py`, `_iterable_mixin.py`, `_set_algebra.py`, `object.py`,
`tests/test_slots.py`, `tests/test_types/test_object.py`, `INFECTIONS.md`.

---

### ~~21. Rebinding a class-side message answers a bare `AttributeError: name`~~ — DONE

**Decision + implemented.** `#name is answered by every class — it cannot be
rebound`, reached by both spellings of the mistake (`Foo.name = 5` and
`Foo.set_attr("name", 5)`). The `set_attr` question the proposal set aside — a
user method silently replaced — is left where it was, as a different decision.
`poop/types/meta.py`, `tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~22. `Bytes` and `ByteArray` refuse the tuple-of-prefixes `Str` accepts~~ — DONE

**Decision + implemented.** `affix_needle` moved to `poop/types/_affix.py` and
is shared by all six `startswith`/`endswith` methods. The scalar branch turned
out not to need widening at all: it was `_faithful` already, and only the `Str`
isinstance test made it string-specific, so the fall-through covers `Bytes` and
`ByteArray` unchanged. `poop/types/_affix.py`, `string.py`, `bytes.py`,
`byte_array.py`, `tests/test_types/test_bytes.py`, `test_byte_array.py`,
`INFECTIONS.md`.

---

### ~~23. A constructor call the converter does not cover falls through to the raw class~~ — DONE

**Decision + implemented.** Every `<builtin>(...)` reaches its converter
whatever its arity, and the shared `refuse_extra_arguments`
(`poop/transformers/_arity.py`) answers `list is built from at most one
collection, got 2 arguments — write a literal for elements`. `_poop_str_from`
grew the decoding form CPython has, delegating to `Bytes.decode` so POOP's
codec table governs it — including the keyword spellings `str(b,
encoding="utf-8")`, which are valid CPython too.

The `dict(1, 2, 3)` row in `tests/test_cloak.py` was the table's own record of
this leak (`dict.__init__()`) and became a pointer to the new
`tests/test_transformers/test_constructor_arity.py`.
`poop/transformers/_arity.py`, `_collection.py`, `dict.py`, `string.py`,
`bytes.py`, `byte_array.py`, `memory_view.py`, `complex.py`, three test
modules, `INFECTIONS.md`.

---

### ~~24. `Str` and `Dict` answer almost none of the iteration protocol the bans point at~~ — DONE

**Decision + implemented, on the recommendation the proposal made.** Both
inherit `_IterableMixin` and override the collisions; `Dict`'s mixin messages
iterate the **keys**, matching CPython's `map(f, d)`, with `d.items().map(...)`
as the pair-shaped spelling and `do` still yielding pairs.

`Str` keeps `find`/`count`/`index` with their string meaning, and all three now
refuse a block with a sentence — arriving from `[1, 2].find(block)` that is
exactly what a reader writes, and CPython answered `find() argument 1 must be
str, not function`. `sum` is refused outright, as the proposal asked.
`examples/basics/string_iteration.py` teaches the string half.
`poop/types/string.py`, `dict.py`, `tests/test_types/test_str.py`,
`test_dict.py`, the example, `README.md`, `INFECTIONS.md`.

---

### ~~25. `Boolean` answers no numeric message, though it computes like an `int`~~ — DONE

**Decision + implemented.** All twenty-odd int-side messages delegate through
`_as_int()`, written out rather than generated, and each answers an `Int` as
CPython does.

`min`/`max` are the one exception to the fold, which the proposal did not
anticipate: they answer one of their *operands*, and `min(True, 5)` is `True` in
CPython, so folding first would have answered `1` for a receiver the program
still holds as a flag. They route through `_minmax` over `(self, *others)`
exactly as `Int` does. `poop/types/boolean.py`,
`tests/test_types/test_boolean.py`, `INFECTIONS.md`.

---

### ~~26. `sorted` exists on two receivers out of fifteen~~ — DONE

**Decision + implemented, sequenced after 24 as the proposal suggested**, which
made it a single method in a single file. `_IterableMixin.sorted` answers a
`List` whatever the receiver, keyword-only; `List` and `Tuple` keep their
overrides, the second answering a `Tuple` on purpose. `Str` and `Dict` reach it
through the mixin. `poop/types/_iterable_mixin.py`, four test modules,
`INFECTIONS.md`.

---

### ~~27. `raise_` is a spelling, not a message — so nothing can be re-raised~~ — DONE

**Decision + implemented.** `class_side` on `PoopExcMeta` gives `raise_` to
every mirror and to every user class descending from one; `PoopMeta` carries the
refusing twin (`A cannot be raised — only a class descending from Exception
can`). `RaiseTransformer` and its test are deleted, retiring the ordering
constraint documented in `INFECTIONS.md` and `CLAUDE.md`.

A computed class, a lowercase binding and — the one that matters — a **re-raise**
from inside a handler all work now. One claim in the proposal did not hold:
`raise_` still does not appear in `dir()`, because `dir(cls)` never merges the
metaclass's names. That is a pre-existing gap for the *whole* class side
(`name`, `superclass`, `print` are invisible too) and is filed as item 33 rather
than folded in here. `poop/types/exceptions.py`, `meta.py`,
`poop/transformers/exception.py`, `__init__.py`, deleted
`poop/transformers/raise_.py` and its test, `tests/test_types/test_exceptions.py`,
`INFECTIONS.md`, `CLAUDE.md`.

---

### ~~28. `x.__init__(...)` re-runs the constructor on a live value~~ — DONE

**Decision + implemented.** `_is_super_call(node.value)` narrows the carve-out
from the name to the syntax it was written for — `allow_init` already existed
as a parameter, and this is the third caller it was built for.
`super().__init__(...)` still parses and runs; every other receiver is refused
at validation time. `poop/validators/no_dunder_attribute.py`,
`tests/test_validators/test_no_dunder_attribute.py`, `INFECTIONS.md`.

---

### ~~29. Every class-side message reports as `PoopMeta.<name>()`~~ — DONE

**Decision + implemented.** `class_side.__set_name__` cloaks its function
through `cloak_callable`, which is the one moment the function knows the message
it answers. `Foo.print(1, 2, 3)` reads `print() takes from 1 to 3 positional
arguments but 4 were given`: no receiver, but no invented one and no internal
name. The alternative — rewording inside `class_side.__get__` — stays recorded
in the proposal's own text rather than implemented. `poop/types/meta.py`,
`tests/test_cloak.py`, `INFECTIONS.md`.

---

### ~~30. `pow` the message is narrower than `**` the operator and `pow` the builtin~~ — DONE

**Decision + implemented.** `poop/types/_pow.py` completes the reflected
protocol before refusing, so `(2).pow(complex(1, 1))` answers what `2 **
complex(1, 1)` and `pow(2, 1+1j)` answer; the modulus form does not reflect,
matching CPython. The refusal's operator wording became `#pow`. `Complex.pow`
was added beside `abs` and `negated`. `Int.divmod` was left alone, as the
proposal insisted. `poop/types/_pow.py`, `int.py`, `float.py`, `complex.py`,
three test modules, `INFECTIONS.md`.

---

### ~~31. `Bytes` and `ByteArray` do not answer `ord`~~ — DONE

**Decision + implemented.** Both answer `ord` now. The wrong-length refusal was
reworded on all three receivers rather than left to CPython as the proposal
suggested: `ord() expected a character, but string of length 2 found` names the
builtin as a call and says `string` for a receiver that prints as bytes, so it
would have failed item 32's sweep the moment it was added. It reads `#ord
expects a single byte, got 2`. `poop/types/bytes.py`, `byte_array.py`,
`string.py`, three test modules, `tests/test_no_python_wording.py`,
`INFECTIONS.md`.

---

### ~~32. The wording sweep is opt-in by program, so four more call-spellings survive~~ — DONE

**Decision + implemented, both halves.** The six sites are reworded —
`complex`'s three type refusals and its malformed string, `int`'s base refusal,
`Int.chr`'s range refusal, and the mutation-during-iteration `RuntimeError`,
caught in `_IterableMixin.do`, `Dict.do` and `_PeekMixin`'s cursor.

The static half walks `poop/types` and `poop/transformers` for every string
literal handed to a `MIRRORS[...]` call and runs `_FORBIDDEN` over it, with one
exemption list for the phrases a message may legitimately quote. Only a
*native* `RuntimeError` is reworded, and the test for that is on `type(exc)`:
`PoopExcMeta` makes a mirror match its native twin on purpose, so `isinstance`
is true of every `RuntimeError` and would have reworded POOP's own messages —
the one trap in this item. `poop/transformers/complex.py`, `int.py`,
`poop/types/int.py`, `_mutated.py`, `_iterable_mixin.py`, `_peek.py`, `dict.py`,
`tests/test_no_python_wording.py` and four test modules, `INFECTIONS.md`.

---

### 33. The class side is invisible to `dir()` and `:methods`

**Severity: low (a documented surface no discovery tool shows).**

`dir(cls)` never merges the metaclass's names — CPython's `type.__dir__` walks
the class's own MRO only — so **none** of the class-side protocol appears in
POOP's introspection substitutes:

```bash
class Foo(Object):
    pass

Foo.dir().includes("name").print()        # -> False
Foo.dir().includes("superclass").print()  # -> False
ValueError.dir().includes("raise_")       # -> False
```

`INFECTIONS.md` already records the half of this that motivated proposal 1
("`dir()` never listed either name, so both were unreachable by reading and
reachable by typing") — but it recorded it about `mro` and `register`, the two
names POOP *refuses*. The same gap hides the **26** it answers — `PoopMeta`
carries 28 `class_side` descriptors, and only `mro` and `register` are refusals:
`name`, `superclass`, `print`, `class_name`, `get_attr`, `is_instance`,
`assert_`, `if_none`, and the rest, plus `raise_`, which item 27 made a message
on `PoopExcMeta`. `:methods` reads the same `dir()`, so the REPL cannot show
them either.

**Solution.** `PoopMeta.dir` (`poop/types/meta.py`) merges the `class_side`
descriptors found on `type(cls).__mro__` into its answer. The refusing ones
must not be listed — offering a name that answers "that is Python's, use
`superclass`" is worse than omitting it — which needs a way to tell a refusal
from a message. The cheap version is a set of names in `meta.py`; the honest
one is a flag on the descriptor (`class_side(fn, refuses=True)`, or a sibling
decorator), so a new refusal cannot be added and forgotten. Prefer the flag,
for the reason `_EXEMPT` in `test_mirrored_raises.py` gives about lists that
have to be kept in step by hand.

Tests under `tests/test_types/test_meta.py` (every answered class-side message
is listed; neither `mro` nor `register` is) and `tests/test_repl.py` (`:methods`
on a class shows them).
