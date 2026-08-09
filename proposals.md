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

### 11. The `at` treatment never reached the messages that *remove* an element

**Severity: medium (Python leak).**

`poop/types/_at.py` exists because every wrapper handed its index straight to
CPython and the learner read Python's own wording back. `at`, `List.pop`,
`List.index` and `List.remove` were reworded; the six messages that remove an
element from a `Dict`, a `Set` or a `ByteArray` were not, and they fail exactly
the way `_at.py`'s docstring quotes as the thing POOP stopped doing:

```bash
d = {"a": 1}
d.pop("b")                # -> KeyError: 'b'
{}.popitem()              # -> KeyError: 'popitem(): dictionary is empty'
{1}.remove(2)             # -> KeyError: 2
set().pop()               # -> KeyError: 'pop from an empty set'
bytearray().pop()         # -> IndexError: pop from empty bytearray
bytearray(b"a").remove(98)  # -> ValueError: value not found in bytearray
```

Three of them are a bare `repr` with no sentence at all — the third example in
`_at.py`'s docstring, verbatim. The other three name the method as a Python
call (`popitem()`, `pop from …`) rather than as a message, and say
`dictionary` where the receiver prints as a `dict`. The same program asking
`d.at("b")` already gets `dict has no key 'b'`, so one receiver answers two
vocabularies depending on which message missed.

**Solution.** `_at.py` already owns this wording and already answers (rather
than raises) its exceptions so a call site can write `from None`. Add the two
missing shapes beside `no_element_at` / `no_element_equal_to`:

```python
def no_key(receiver: object, key: Any) -> Exception:
    """The mirrored `KeyError` for a key the receiver does not hold."""
    return MIRRORS["KeyError"](f"{type(receiver).__name__} has no key {key!r}")


def nothing_to_remove(receiver: object) -> Exception:
    """The mirrored refusal for a removal from an empty receiver."""
    return MIRRORS["KeyError"](
        f"{type(receiver).__name__} has no element to remove — it is empty"
    )
```

`at_key` already composes the first sentence for `Dict.at`; factor its message
through `no_key` so the two cannot drift. Then wrap the six call sites in
`try/except` and `raise … from None`, as `List.pop` does — `Dict.pop`,
`Dict.popitem` (`poop/types/dict.py`), `Set.remove`, `Set.pop`
(`poop/types/set.py`), `ByteArray.pop`, `ByteArray.remove`
(`poop/types/byte_array.py`). `ByteArray.pop` is the one that already has a
twin to copy verbatim: `List.pop` raises `no_element_at` for the index form and
"has no element to remove — it is empty" for the bare one.

`Dict.pop(key, default)` and `Set.discard` must stay untouched — they are the
spellings that *ask* rather than assert, and neither raises today.

Tests: one per site under `tests/test_types/test_dict.py`, `test_set.py`,
`test_byte_array.py`, plus the six programs added to
`tests/test_no_python_wording.py` — `popitem()`, `pop from` and `bytearray`
are precisely what that sweep is for. `INFECTIONS.md` beside the `at` entry.

---

### 12. Python's *call* syntax survives inside `min` / `max` / `zip` diagnostics

**Severity: low (Python leak).**

POOP's substitute for `min(xs)` is the message `xs.min()`, and for `zip(a, b)`
the message `a.zip(b)`. When either fails, CPython's own wording comes back —
naming the free function POOP forbids, with the parentheses of a call the
program never wrote:

```bash
[].min()                                   # -> ValueError: min() iterable argument is empty
[1, 2].zip([1], strict=True).do(block)     # -> ValueError: zip() argument 2 is shorter than argument 1
```

An empty collection is not an exotic input, and `min()` is a name
`no_min` rejects on sight two lines earlier in the same file. The `zip` message
additionally numbers its arguments from the *call*'s perspective — "argument 2"
is the first argument the program actually passed, since the receiver is
argument 1.

**Solution.** Both diagnostics belong to the wrapper that owns the message.
In `_minmax` (`poop/types/_minmax.py`), catch the empty case rather than
letting CPython describe it — the helper already knows whether a `default` was
given, which is the whole condition:

```python
    try:
        return func(iterable, **kwargs)
    except ValueError:
        raise MIRRORS["ValueError"](
            f"{name} of an empty collection is undefined — "
            "send it a default instead"
        ) from None
```

with `name` being `#min` / `#max`, passed in by the caller (the helper takes
`func`, so it must not read `func.__name__` — that spells the builtin).
`_minmax` deliberately imports no POOP module at the top; `MIRRORS` is reachable
the same function-local way `_is_absent` already is.

For `Zip` (`poop/types/zip.py`), `_gen` is the one place the native `zip` runs,
so the same `except ValueError` there can reword both directions of the strict
mismatch in terms of the receiver and the ordinal of the *argument as sent*:
`the 1st argument ran out before the receiver`.

Tests under `tests/test_types/test_list.py`, `test_dict.py`, `test_string.py`
(the three receivers that reach `_minmax` with a collection) and
`test_zip.py`, plus both programs in `tests/test_no_python_wording.py`.

---

### 13. `key` and `default` are still positional on every collection `min` / `max`

**Severity: medium (silent wrong answer).**

Proposal 3 made `key` keyword-only on `Int.min` / `Int.max` / `Float.*`, and
proposal 9 did the same for `sorted` / `sort`, both for one reason: positionally
a block is indistinguishable from a value. The collection rungs were never
converted, and CPython spells them keyword-only too —
`min(iterable, *, key=None, default=…)`:

```python
def min(self, key=None, default=_MISSING) -> Any:   # _iterable_mixin, Dict, Str
```

So `xs.min(0)` — the plain reading of "the smallest, or 0 if empty", and the
exact shape `Dict.get`/`Dict.pop`/`List.pop` all take positionally — hands `0`
to the *key* slot:

```bash
[1, 2].min(0)   # -> TypeError: 'int' object is not callable
[].min(0)       # -> ValueError: min() iterable argument is empty
```

The first is merely confusing; the second is the failure proposal 3 called out
by name — a *comparable* argument in the key slot answers a plausible wrong
number in silence. `[[3], [1]].min([9])` is the same shape and does not raise
at all.

**Solution.** Make both parameters keyword-only in `_IterableMixin.min` /
`.max` (`poop/types/_iterable_mixin.py`), `Dict.min` / `.max`
(`poop/types/dict.py`) and `Str.min` / `.max` (`poop/types/string.py`):

```python
    def min(self, *, key=None, default=_MISSING) -> Any:
```

This is the "a substitute mirrors the builtin's full Python signature" rule the
last two proposals both closed on, and it is a breaking change of the same
size: nothing in `examples/` passes either argument positionally, and the suite
has four call sites (`tests/test_types/test_list.py`, `test_dict.py`,
`test_string.py`) that do and become the refusal tests. `Int`/`Float` keep
their variadic `*others` form, which is a different signature and already
correct. `INFECTIONS.md` beside the `min`/`max` rows.

---

### 14. `List.index` silently ignores `stop` when `start` is absent

**Severity: medium (silent wrong answer).**

`List.index` branches on which optional arguments are present, and the first
branch swallows both:

```python
        if _is_absent(start):
            return Int(self._items.index(obj))     # `stop` dropped on the floor
        if _is_absent(stop):
            return Int(self._items.index(obj, _opt_int(start, 0)))
        return Int(self._items.index(obj, _opt_int(start, 0), _opt_int(stop, 0)))
```

Both are ordinary positional-or-keyword parameters, so `stop` is nameable, and
naming it alone answers a wrong number instead of refusing:

```bash
[1, 2, 3].index(3, stop=1).print()   # -> 2, where Python's [1,2,3].index(3,0,1) raises
```

The same slip sits in the third branch's default: `_opt_int(stop, 0)` reads an
explicit `none` as *stop at 0*, which makes every search fail — the reverse of
`start`'s `0`, where 0 is the right default. `Tuple.index`, `Str.index` and
`Bytes.index` do not have the bug; they pass `_unwrap(..., None)` straight
through, which is the shape that works.

**Solution.** Drop the branching and let `None` mean "no bound", as CPython's
own default does and as the other three wrappers already do:

```python
        try:
            return Int(
                self._items.index(
                    obj, _opt_int(start, 0), _opt_int(stop, len(self._items))
                )
            )
        except ValueError:
            raise no_element_equal_to(self, obj) from None
```

`len(self._items)` rather than `None`, because `list.index` — unlike
`str.index` — takes no `None` bound. Same fix for `ByteArray.index` if it
carries the same branching (`poop/types/byte_array.py`). Tests under
`tests/test_types/test_list.py`: `stop` alone, `stop=none`, and a bound that
excludes the only match.

---

### 15. `reversed` answers a different kind for `Str`, and does not exist for `Bytes`

**Severity: medium (inconsistent surface + a ban with no substitute).**

`no_reversed` forbids `reversed(col)` and points at `col.reversed()`. Every
receiver answers its own kind — `List` → `List`, `Tuple` → `Tuple`, `Range` →
`Range` (proposal 10 made the sliced form match), the dict views → their
reverse iterators — except `Str`, which answers a `List` of one-character
`Str`s:

```bash
"abc".reversed().print()   # -> c b a   (a List, printed element by element)
```

`"abc".slice(...)` answers a `Str` and `"abc".at(0)` answers a `Str`, so
`reversed` is the one message on that receiver that changes the type, and
`s.reversed().upper()` fails where every other chain composes. This is the same
shape as proposal 4's finding: one selector meaning two things depending on the
receiver.

`Bytes` and `ByteArray` answer nothing at all:

```bash
b"abc".reversed()            # -> bytes does not understand #reversed
bytearray(b"abc").reversed() # -> bytearray does not understand #reversed — did you mean #reverse?
```

Python reverses both (`bytes` is a sequence), so the validator bans a construct
whose substitute does not exist — the one thing CONTRIBUTING's "activate a
validator only when the substitute exists" rule forbids. The `did you mean
#reverse?` hint is worse than nothing: it points at the *in-place* mutation on
`ByteArray`, and at nothing at all on immutable `Bytes`.

**Solution.** Two changes, one commit each.

1. `Str.reversed` (`poop/types/string.py:150`) answers a `Str`:
   `return Str(self._value[::-1])`. The `List`-of-characters spelling stays
   reachable as `s.reversed().list()` for anyone who wanted it.
2. Add `Bytes.reversed` → `Bytes` and `ByteArray.reversed` → `ByteArray`
   (`self._value[::-1]`), sitting beside `ByteArray.reverse`, whose docstring
   should name the difference the way `List.reverse`/`List.reversed` do.

Two more receivers have the same hole and belong in the second commit:
`reversed(d)` and `reversed(memoryview(b"ab"))` both work in CPython, and
neither `Dict` nor `MemoryView` answers `#reversed` — though `DictKeys` does,
so `Dict.reversed` is one line delegating to `self.keys().reversed()` (a
`DictReverseKeyIterator`, which is what `reversed(d)` yields).

All of these are behaviour changes to a documented message, so `INFECTIONS.md`
and any example using `"…".reversed()` must move in the same commits. Tests
under `tests/test_types/test_string.py`, `test_bytes.py`, `test_byte_array.py`,
`test_dict.py`, `test_memory_view.py`.

---

### 16. `MemoryView` prints the raw memory address

**Severity: low (Python leak).**

`MemoryView.__str__` is `repr(self._value)`, so the object prints CPython's own
form:

```bash
memoryview(b"ab").print()   # -> <memory at 0x70cb7ab59240>
```

That is the pointer `Object.__hash__` refuses to answer — its comment says so in
as many words: answering the address "made `x.hash()` print the raw pointer POOP
otherwise never admits exists". It also names the class `memory`, which is
neither the POOP name nor the cloak (`memoryview`), and it is unstable across
runs, so no test can pin it and no example can show it.

**Solution.** Print what the view *is*, in the shape every other wrapper uses —
the class name and the data it exposes:

```python
    def __str__(self) -> str:
        return f"<memoryview of {self._value.nbytes} bytes>"
```

The alternative — printing the bytes themselves, `memoryview(b'ab')` — reads
better for a small buffer but re-materializes an arbitrarily large one just to
print it, which is the cost proposal 10 refused. Prefer the summary.

The same receiver is missing three messages that the bans point at, and they
belong in the same commit, since "a `MemoryView` you cannot look into" is one
gap with four spellings:

- `hex()` — CPython has it, and with `__str__` summarizing there would
  otherwise be *no* message that shows the contents at all.
- `slice(...)` — `mv[0:2]` is a `memoryview` in CPython, `no_subscript` names
  `.slice(...)` as the substitute, and every other sequence answers it.
- `includes(x)` — `98 in memoryview(b"ab")` is `True` in CPython, and `no_in`
  names `col.includes(x)`.

`poop/types/memory_view.py`, `tests/test_types/test_memory_view.py`,
`INFECTIONS.md`.

---

### 17. REPL tab-completion advertises the internals every other surface hides

**Severity: medium (encapsulation leak).**

`Object.dir()` filters every `_`-prefixed name, and its comment says why — "so
the introspection substitute never surfaces what the encapsulation rules hide.
Same predicate as the REPL's `:methods`". `_reject_private` enforces the same
rule at runtime for `get_attr`. The REPL's completer uses a *different*
predicate — `not name.startswith("__")` — so pressing Tab offers exactly the
names the other three refuse:

```python
>>> from poop.repl import _PoopCompleter
>>> _PoopCompleter({"x": Str("abc")})._attr_matches("x._")
['x._abc_impl', 'x._checked_name(', 'x._eq_attr', 'x._eq_comparable(',
 'x._eq_group', 'x._reject_dunder(', 'x._reject_private(', 'x._value']
```

`x._value` is the raw Python `str` behind the wrapper — the one thing
`_reject_private` exists to keep out of user code — and `_abc_impl` and
`_eq_group` are POOP internals with no meaning in the language at all. Plain
attribute access still reaches them (proposal 6 measured that leak and accepted
it), which is what makes this worse than cosmetic: the REPL is *teaching* the
spelling.

`_name_matches`, one method up, filters `_poop_`-prefixed bindings only, so a
bare-name completion still offers any other `_`-prefixed key.

**Solution.** One predicate, in one place, shared by all four call sites:

```python
def _is_message(name: str) -> bool:
    """A name user code may send. The predicate `Object.dir()` uses."""
    return not name.startswith("_")
```

Put it beside `MessageNotUnderstood`'s neighbours in `poop/types/object.py` (or
in `_selectors.py`, which already owns the `:methods` hint machinery), then use
it from `Object.dir`, `Repl._meta_methods`, `_PoopCompleter._attr_matches` and
`_PoopCompleter._name_matches`. The duplication is the bug: three copies of one
rule drifted, and only the copy nobody tested drifted.

While there, `_attr_matches` calls `getattr(obj, name, None)` on every candidate
purely to decide whether to append `(` — which *runs* a `property` getter on a
user class, so pressing Tab can execute program code. Reading the attribute off
the type (`getattr(type(obj), name, None)`) answers the same question without
invoking a descriptor.

Tests under `tests/test_repl.py`: `_attr_matches("x._")` is empty for a `Str`,
`_name_matches("_")` offers nothing, and a class with a side-effecting
`property` is not triggered by completion.

---

### 18. `Range.index` still answers the sentence `_at.py` was written to delete

**Severity: low (Python leak).**

`no_element_equal_to`'s docstring quotes the wording it replaced: "CPython
spelled this as `list.index(x): x not in list` — the method written as a Python
call rather than sent as a message, and the placeholder `x` where the value the
reader passed belongs." `List.index`, `Tuple.index` and `Str.index` all route
through it. `Range.index` does not, and answers the quoted sentence with only
the noun changed:

```bash
range(5).index(9)   # -> ValueError: range.index(x): x not in range
(1, 2).index(9)     # -> ValueError: tuple has no element equal to 9
```

`Range.count`, one line above it, cannot fail, so `index` is the whole of the
gap. It was missed because `Range` reaches `_at.py` for `at` only — `at_index`
is imported, `no_element_equal_to` is not.

**Solution.** The same three lines every other sequence uses:

```python
    def index(self, value: Int) -> Int:
        try:
            return Int(self._range().index(_faithful(value)))
        except ValueError:
            raise no_element_equal_to(self, value) from None
```

`self`, not `self._range()`, as the receiver — `at` already passes the POOP
`Range` for this reason, so the name in the message is the one the reader
wrote. `poop/types/range.py`, `tests/test_types/test_range.py`, and the program
in `tests/test_no_python_wording.py`, which `range.index(x)` trips on two
counts.

---

### 19. `Try` and `With` report a non-block argument in Python's calling vocabulary

**Severity: low (Python leak, on the two constructs POOP hands users directly).**

`Try` and `With` are the only two names `DEFAULT_NAMESPACE` exposes, and each
takes a block it defers. Hand either one something that is not a block and the
refusal comes from CPython's call machinery, one frame deep, naming a
convention POOP has no word for:

```bash
Try(5).run()                       # -> TypeError: 'int' object is not callable
Try(lambda: risky()).except_(Exception, 5).run()  # -> same
With(5).do(block)                  # -> same
With(a_manager).do(block)          # -> TypeError: 'C' object is not callable
```

The last one is the mistake worth optimizing for: `With` takes a block that
*answers* a context manager (`With(lambda: lock)`), and passing the manager
itself is the obvious first attempt — the docstring's own usage lines are the
only thing that says otherwise. The reader is told their object is not
callable, which is true of every POOP object and says nothing about what was
expected.

`Block` already established the rule for this: its `__call__` catches the
arity `TypeError` and rewords it, "because CPython's wording is the leak. It
says `<lambda>()` … and `positional argument`, a calling convention a block
does not have."

**Solution.** Check at the boundary, where the argument is named, rather than
at the call. In `Try.__init__`, `Try.except_` (the handler) and `With.__init__`:

```python
def _block(value: Any, role: str, hint: str) -> Any:
    if not callable(value):
        raise MIRRORS["TypeError"](
            f"{role} must be a block, got {article(type(value).__name__)} — {hint}"
        )
    return value
```

with hints that show the spelling: `Try(lambda: …)`, `.except_(ValueError,
lambda e: …)`, `With(lambda: …)`. `article` already exists in
`poop/types/_message.py` and is what `Int.pow`'s modulus refusal uses.

Checking in `__init__` rather than in `run`/`do` is the point — it is the same
argument proposal 2 settled for `With`: resolve what you need before running
anything, so the failure lands where the mistake was written instead of after a
deferred block has already had side effects. `poop/types/try_.py`,
`poop/types/with_.py`, `tests/test_types/test_try_.py`,
`tests/test_types/test_with_.py`, `INFECTIONS.md`.

---

### 20. Three slot-less mixins give 36 of 49 wrappers a `__dict__` they declared away

**Severity: high (state on value objects, and a third of the memory).**

Every wrapper declares `__slots__` — CONTRIBUTING makes it step 1 of adding a
type. Three shared bases do not: `_ValueEqMixin` (`_value_eq.py`),
`_IterableMixin` (`_iterable_mixin.py`) and `_SetAlgebraMixin`
(`_set_algebra.py`). One slot-less class anywhere in an MRO restores the
per-instance `__dict__` for everything below it, so the declaration is defeated
on **36 of the 49 POOP classes** — `Str`, `List`, `Tuple`, `Dict`, `Set`,
`FrozenSet`, `Bytes`, `ByteArray`, `Range`, `MemoryView`, every dict view and
every iterator. `_NumericCompareMixin` and `_PeekMixin` do declare `__slots__`,
which is why `Int`, `Float`, `Boolean` and `Complex` are the ones that behave.

It is user-visible, and it makes `set_attr` mean two different things on two
rungs of the same tower:

```bash
"abc".set_attr("x", 1)   # succeeds. get_attr("x") answers 1, and dir() lists x
[1].set_attr("tag", "a") # succeeds — arbitrary state on a list
(1,).set_attr("tag", "a")# succeeds — arbitrary state on a *tuple*
(5).set_attr("x", 1)     # AttributeError: 'int' object has no attribute 'x'
                         #   and no __dict__ for setting new attributes
```

So a value object accepts attached state; two `Str`s that compare equal carry
different attributes; and the refusal, where it happens, spells `__dict__` —
a dunder `no_dunder_attribute` bans and `Object._reject_dunder` will not even
let a program name.

**Solution.** Three lines, one per mixin:

```python
class _ValueEqMixin:
    __slots__ = ()
```

Verified on a patched build: `Str` drops from 56 to 40 bytes (the same as
`Int`), 100 000 `Str` values drop from 14.2 MB to 9.4 MB — **34% less** — no
wrapper carries a `__dict__` any more, and the whole suite still passes
(3439 tests, 100% coverage, no test touched). An empty `__slots__` on a mixin
cannot collide with the concrete class's own slots, which is what makes it
safe across all 36.

The fix exposes a second half, which belongs in the same proposal because the
first half causes it: with the `__dict__` gone, `"abc".set_attr("x", 1)` starts
answering CPython's `'str' object has no attribute 'x' and no __dict__ for
setting new attributes` — the message quoted above, now on every wrapper.
`Object.set_attr` must catch it and say so in POOP's vocabulary, naming the
distinction that is actually being drawn:

```python
        try:
            builtins.setattr(self, raw, value)
        except AttributeError:
            raise MIRRORS["AttributeError"](
                f"{type(self).__name__} is a value — it holds no state of its "
                "own; only an object of a class you defined can be given one"
            ) from None
```

User classes are unaffected: `ClassTransformer` builds them without
`__slots__`, so `self.count = 1` and `set_attr` keep working there — which is
the line POOP wants drawn anyway. `poop/types/_value_eq.py`,
`_iterable_mixin.py`, `_set_algebra.py`, `object.py`; tests under
`tests/test_types/test_object.py` (a wrapper refuses attached state, a user
class accepts it) and a sweep test asserting no POOP class carries a
`__dict__`, which is what keeps the next mixin from reopening it.
`INFECTIONS.md` beside the encapsulation rules.

---

### 21. Rebinding a class-side message answers a bare `AttributeError: name`

**Severity: low (diagnostic with no sentence).**

`class_side.__set__` exists so a data descriptor wins the lookup, and it
refuses assignment by raising `MIRRORS["AttributeError"](self._name)` — the
name and nothing else:

```bash
class Foo(Object):
    pass

Foo.name = 5              # -> AttributeError: name
Foo.set_attr("name", 5)   # -> AttributeError: name
```

`AttributeError: name` reads as if the *word* `name` were the problem. It says
neither what was refused nor why, and both spellings of the mistake — the
assignment and the sanctioned `set_attr` substitute — land on it. Every other
refusal in the language carries a sentence; `_reject_private`, ten lines away
in the same file, is the model.

**Solution.** Say what the class side is:

```python
    def __set__(self, cls: type, value: object) -> None:
        raise MIRRORS["AttributeError"](
            f"#{self._name} is answered by every class — it cannot be rebound"
        )
```

`poop/types/meta.py`, `tests/test_types/test_meta.py`. Worth checking the same
message on a *user* method name while there: `Foo.set_attr("m", block)` for a
method `Foo` defines itself is allowed today and silently replaces it, which
may deserve its own decision — but it is a different question from this one and
should not be folded in.

---

### 22. `Bytes` and `ByteArray` refuse the tuple-of-prefixes `Str` accepts

**Severity: medium (a ban with no substitute on two receivers).**

`_affix_needle` in `poop/types/string.py` maps a POOP `Tuple` to a Python tuple
of prefixes, and its docstring says why that shape has to exist: "CPython
accepts a tuple of prefixes, and in POOP that is the only message-shaped
substitute for the forbidden `s.startswith("a") or s.startswith("b")`". `Bytes`
and `ByteArray` pass their argument through plain `_faithful`, so the same
program on the same data fails:

```bash
"ab".startswith(("a", "z"))     # -> True
b"ab".startswith((b"a", b"z"))  # -> TypeError: startswith first arg must be
                                #    bytes or a tuple of bytes, not tuple
```

The refusal is also self-contradicting from where the reader stands: they
*did* pass a tuple, and the sentence tells them a tuple is not a tuple —
CPython is describing its own `tuple`, which a POOP `Tuple` is not. And with
`or` banned, there is no other way to ask the question on bytes.

**Solution.** `_affix_needle` is not string-specific; only its `Str` branch is.
Move it to a shared module (`poop/types/_affix.py`, the way `_at`, `_minmax`
and `_repeat` already factor a rule used by several wrappers), widen the
scalar branch to `Str | Bytes | ByteArray`, and call it from all six methods:
`Str.startswith` / `.endswith`, `Bytes.startswith` / `.endswith`,
`ByteArray.startswith` / `.endswith`. The `Tuple` branch is unchanged — it
already unwraps members through `_faithful` so a wrong-typed member reaches
CPython and raises the faithful error rather than being silently coerced.

Tests under `tests/test_types/test_bytes.py` and `test_byte_array.py` (a tuple
of prefixes, a tuple with a wrong-typed member, an empty tuple — `False` in
CPython), and `INFECTIONS.md`, whose `startswith` rows should stop being true
of `Str` only.

---

### 23. A constructor call the converter does not cover falls through to the raw class

**Severity: high (silent wrong answers).**

`CollectionRewriter.visit_Call` rewrites `list(x)` to the converter binding
only when the call has no keywords and at most one argument. Anything else
falls through to `visit_Name`, which renames the bare builtin to the *class*
binding — and the class constructor is variadic, `List(*elements)`. So the same
name means "convert" at one arity and "build from these elements" at another,
and only the first matches Python:

```bash
list(1, 2).print()        # -> 1 2          CPython: list expected at most 1 argument, got 2
tuple(1, 2).print()       # -> 1 2          CPython: tuple expected at most 1 argument, got 2
set(1, 2).print()         # -> {1, 2}       CPython: set expected at most 1 argument, got 2
frozenset(1, 2).print()   # -> frozenset({1, 2})
list(5)                   # -> TypeError: cannot convert int to list   (correct!)
```

`list(a, b)` is a plausible slip for `[a, b]`, and CPython exists to catch it.
Here it is accepted and answers something — which is the failure mode POOP's
own diagnostics work hardest to avoid.

The scalar wrappers fall through the same way, and there the answer is not
wrong but the report is:

```bash
str(b"ab", "utf-8")   # -> TypeError: str.__init__() takes 2 positional arguments but 3 were given
complex(1, 2, 3)      # -> TypeError: complex.__init__() takes 2 positional arguments but 4 were given
memoryview(b"ab", 1)  # -> TypeError: memoryview.__init__() takes 2 ...
bytearray("ab", "utf-8", "strict")  # -> TypeError: bytearray.__init__() takes from 1 to 2 ...
```

Every one of those names `__init__` — the dunder `no_dunder_attribute` bans
outright — from a construct the program spelled without a dunder anywhere.
(`str(b"ab", "utf-8")` is also a *valid* CPython call, answering `"ab"`, so the
converter is under-powered as well as badly reported.)

**Solution.** The fall-through is the bug: a call to a builtin's name must
never resolve to the wrapper class. Two changes, one commit each:

1. In `CollectionRewriter.visit_Call` (and the `bytes`/`str`/`complex`/… twins),
   rewrite the call to the converter binding **regardless of arity**, passing
   the arguments through, and let the converter refuse:

   ```python
   def _from(*args: object) -> T:
       if len(args) > 1:
           raise MIRRORS["TypeError"](
               f"{poop_type.__name__} is built from at most one collection, "
               f"got {len(args)} arguments — write a literal for elements"
           )
   ```

   which is CPython's rule stated in POOP's vocabulary, and points at the
   literal that is the right spelling for `list(1, 2)`.
2. Widen `_poop_str_from` to the two-argument `str(bytes, encoding)` form
   `Str.decode` already implements, so the converter covers what the builtin
   covers rather than deferring to a class whose `__init__` does not.

The `visit_Name` rename must stay — a bare `list` used as a value still has to
answer POOP's class — but with the call path complete it stops being reachable
by a *call*. Tests: the multi-argument form of each of the five collections and
of `str`/`complex`/`memoryview`/`bytearray` under
`tests/test_transformers/`, and the `__init__` spellings added to
`tests/test_no_python_wording.py`, which is what would have caught this.

---

### 24. `Str` and `Dict` answer almost none of the iteration protocol the bans point at

**Severity: high (bans with no substitute, on the two most common receivers).**

`no_map`, `no_filter`, `no_all`, `no_any`, `no_sum` and `no_loops` each name a
message on the collection as the substitute (`col.map(block)`, `col.all(block)`,
`col.sum()`, and `do` for `for`). `_IterableMixin` supplies all of them — and
neither `Str` nor `Dict` inherits it:

```bash
"abc".do(block)        # -> str does not understand #do
"abc".map(block)       # -> str does not understand #map
"abc".all(block)       # -> str does not understand #all
"ab".enumerate()       # -> str does not understand #enumerate
"ab".zip("cd")         # -> str does not understand #zip
{"a": 1}.map(block)    # -> dict does not understand #map
{"a": 1}.all(block)    # -> dict does not understand #all
{"a": 1}.sum()         # -> dict does not understand #sum
{"a": 1}.filter(block) # -> dict does not understand #filter — did you mean #iter?
```

`Bytes`, `ByteArray`, `Range`, `MemoryView`, `Set`, `List`, `Tuple` and every
dict view answer all of them. A string is the most-written receiver in the
language, and iterating one means driving the cursor by hand
(`(lambda: it.has_next()).while_true(...)`) because `for` is banned — the exact
situation INFECTIONS' own principle forbids: "Activate validator only when the
substitute exists".

`Dict` is the deliberate half of the omission — it defines `do` over `Tuple(k,
v)` pairs, plus `min`/`max`/`enumerate`/`zip` — so the mixin's `do` would have
to stay overridden. `Str` is the accidental half, and its collision is real but
narrow: `Str.find(sub)` means substring search and `_IterableMixin.find(block)`
means first match; `count`/`index` collide the same way.

**Solution.** Add the non-colliding messages to both, rather than the mixin
wholesale:

- `Str`: `do`, `map`, `filter`, `filter_false`, `reduce`, `all`, `any`,
  `enumerate`, `zip` — each yielding one-character `Str`s, which `__iter__`
  already does. Not `sum` (`sum("ab")` is a TypeError in CPython), and not
  `find`/`count`/`index`, which keep their string meanings.
- `Dict`: `map`, `filter`, `filter_false`, `find`, `reduce`, `sum`, `all`,
  `any` over the same thing CPython iterates — the keys — except that `do`
  already iterates pairs, so the block signature must be documented per
  message rather than assumed.

Both can inherit `_IterableMixin` and override the collisions, which is what
`Dict` already does for `do`; that keeps one implementation of nine messages.
The `Dict` keys-vs-pairs split is the one design question worth settling before
implementing — `d.map(block)` over keys matches CPython's `map(f, d)`, while
`d.do` over pairs matches how POOP already teaches dict iteration, and the two
readings cannot both be right. Recommend keys, with `d.items().map(...)` as the
pair-shaped spelling that already works.

`poop/types/string.py`, `poop/types/dict.py`, tests under
`tests/test_types/test_string.py` and `test_dict.py`, `INFECTIONS.md`, and an
example in `examples/basics/` iterating a string, which is currently
unwriteable without the cursor.

---

### 25. `Boolean` answers no numeric message, though it computes like an `int`

**Severity: medium (a ban with no substitute).**

POOP keeps `Boolean` out of `Int`'s subtree deliberately — `_index.py` says so:
"POOP's `Boolean` is not an `Int` subclass — the two rungs of the tower are
separate classes". Everything that makes `bool` an `int` in CPython was then
re-supplied by hand: arithmetic (`True + True` is `2`), reflected arithmetic
(`3 - True` is `2`), comparison across the tower, and `__index__` so
`[10, 20].at(True)` is `20`. The *messages* were not:

```bash
True.abs()          # -> bool does not understand #abs
True.bit_length()   # -> bool does not understand #bit_length
True.divmod(2)      # -> bool does not understand #divmod
True.pow(2)         # -> bool does not understand #pow
True.round()        # -> bool does not understand #round
True.bin()          # -> bool does not understand #bin
True.min(5)         # -> bool does not understand #min
True.to_bytes()     # -> bool does not understand #to_bytes
True.real()         # -> bool does not understand #real
```

All nine work on `bool` in CPython, and each is the *substitute* a validator
names: `no_abs` → `x.abs()`, `no_divmod` → `a.divmod(b)`, `no_pow` →
`a.pow(b)`, `no_round` → `x.round()`, `no_bin` → `x.bin()`. So a program that
was told to stop writing `abs(flag)` has nowhere to go.

**Solution.** `Boolean._as_int()` already exists and is exactly the fold the
arithmetic operators use. Delegate the int-side messages through it, in the
abstract `Boolean` (not in `TrueClass`/`FalseClass`, which would duplicate
every one):

```python
    def abs(self) -> Int:
        return self._as_int().abs()

    def bit_length(self) -> Int:
        return self._as_int().bit_length()
```

…and the same for `bit_count`, `divmod`, `pow`, `round`, `ceil`, `floor`,
`trunc`, `bin`, `hex`, `oct`, `chr`, `to_bytes`, `as_integer_ratio`,
`is_integer`, `real`, `imag`, `numerator`, `denominator`, `conjugate`,
`negated`, `bit_invert`, and `min`/`max` with their variadic `*others`. Each
answers an `Int`, as CPython does (`abs(True)` is `1`, not `True`) — the one
place to be careful, since answering a `Boolean` would be a quiet type error.

A generated loop over a name list would be shorter but would defeat `ty` and
`:methods`; write them out, as `Int` and `Float` already do for each other's
overlap. `poop/types/boolean.py`, `tests/test_types/test_boolean.py`,
`INFECTIONS.md` (the numeric-tower table currently implies `Boolean` has no
int side, which is the assumption this fixes).

---

### 26. `sorted` exists on two receivers out of fifteen

**Severity: medium (a ban with no substitute).**

`no_sorted` forbids `sorted(col)` and names `col.sorted()`. CPython's `sorted`
takes *any* iterable; POOP's message exists on `List` and `Tuple` only:

```bash
{2, 1}.sorted()               # -> set does not understand #sorted
"ba".sorted()                 # -> str does not understand #sorted
range(3).sorted()             # -> range does not understand #sorted
b"ba".sorted()                # -> bytes does not understand #sorted
{"b": 1, "a": 2}.sorted()     # -> dict does not understand #sorted
{"b": 1}.keys().sorted()      # -> dict_keys does not understand #sorted
```

`sorted(s)` is the ordinary way to look at an unordered collection in order,
and a `Set` is where the need is sharpest — it is the one receiver whose own
iteration order a program must not rely on. Every one of these is banned with
nowhere to go.

**Solution.** `sorted` belongs in `_IterableMixin`, next to `min`/`max`, which
solved the identical problem for the identical set of receivers:

```python
    def sorted(
        self,
        *,
        key: Callable[[Any], Any] | NoneClass | None = None,
        reverse: Boolean = false,
    ) -> List:
        from poop.types.list import List

        return List(*_sorted(self._iter_items(), key, reverse))
```

Keyword-only, as proposal 9 settled. It answers a `List` — CPython's `sorted`
always answers a `list`, whatever it was handed — and `List.sorted` /
`Tuple.sorted` keep their existing overrides, the second of which answers a
`Tuple` on purpose (a tuple can hold an order, so preserving the type is the
same call proposal 10 made for a sliced `Range`).

`Str` and `Dict` reach it only once proposal 24 gives them the mixin; until
then they each need the four-line copy, or 24 lands first — worth sequencing,
since doing 24 first makes this one a single method in a single file.

`poop/types/_iterable_mixin.py`, tests under `tests/test_types/test_set.py`,
`test_range.py`, `test_bytes.py`, `test_dict_keys.py`, and `INFECTIONS.md`,
whose `sorted` row should name the mixin rather than the two wrappers.

---

### 27. `raise_` is a spelling, not a message — so nothing can be re-raised

**Severity: high (the substitute for `raise` is unreachable from most of the
language, and re-raising is impossible).**

`RaiseTransformer` rewrites `UppercaseName.raise_(...)` at parse time and
nothing defines `raise_` anywhere. The rewrite fires only when the receiver is
a literal `ast.Name` starting with a capital, so every other way of naming the
same class fails — and fails by saying something untrue about the object:

```bash
err = ValueError
err.raise_("boom")             # -> ValueError does not understand #raise_

d.at("e").raise_("boom")       # -> ValueError does not understand #raise_

Try(lambda: ValueError.raise_("boom")).except_(
    ValueError, lambda e: e.kind().raise_(e.message())
).run()                        # -> ValueError does not understand #raise_
```

The third is the one that matters: `Try` swallows an exception as soon as a
handler matches, `raise` is banned, and `e.kind()` is exactly the class object
POOP added so a handler could name what it caught. **There is no way to
re-raise, or to raise a class a program computed** — every exception must be
spelled as a capitalized literal at the raise site.

`INFECTIONS.md` states the tradeoff as "lowercase `obj.raise_()` is passed
through to the object's own method at runtime", but there is no such method to
pass through to: `dir()` on an exception class does not list `raise_`, so
`:methods` cannot show it, and the substitute `no_raise` points at is
invisible to the discovery tools POOP built for exactly this.

The transformer is also unguarded about what it rewrites — any capitalized
receiver is assumed raisable:

```bash
class A(Object):
    pass

A.raise_("x")   # -> TypeError: A() takes no arguments
```

which reports the constructor of a class the program never asked to build.

**Solution.** Make `raise_` a real class-side message and delete the rewrite.
`class_side` on `PoopExcMeta` (`poop/types/exceptions.py`) gives it to every
mirror and to every user class descending from one, and to nothing else:

```python
class PoopExcMeta(PoopMeta):
    @class_side
    def raise_(cls, *args: Any, **kwargs: Any) -> Never:
        raise cls(*args, **kwargs)
```

Everything the transformer bought stays: it is an expression, so it still works
inside a `lambda` (which was the whole reason for `_poop_raise`); `**kwargs`
still ride along; `ValueError.raise_("x")` is untouched, since
`ExceptionTransformer` rewrites the name to the mirror and the mirror answers
the message. What changes is that `err.raise_(...)`, `d.at("e").raise_(...)`
and `e.kind().raise_(...)` start working — the last one making a re-raise
expressible for the first time — and that `raise_` shows up in `dir()` and
`:methods`.

`PoopMeta` should grow the refusing twin, so the non-exception case reports
what is wrong instead of a constructor error:

```python
    @class_side
    def raise_(cls, *args: Any, **kwargs: Any) -> Never:
        _refuse_native(cls, "raise_", "…")  # or a bespoke message:
        # "A cannot be raised — only a class descending from Exception can"
```

Removing `RaiseTransformer` also retires the ordering constraint
`INFECTIONS.md` documents ("`ExceptionTransformer` **must run after**
`RaiseTransformer`"), which exists only because the rewrite matched on the
name's spelling.

`poop/types/exceptions.py`, `poop/types/meta.py`, delete
`poop/transformers/raise_.py` and its registration, `tests/test_types/`
(a computed class, a lowercase binding, a re-raise from a handler, a
non-exception class), delete `tests/test_transformers/test_raise_.py`, and
rewrite the `Raise` section of `INFECTIONS.md` — including the tradeoff note,
which describes a passthrough that never existed.

---

### 28. `x.__init__(...)` re-runs the constructor on a live value

**Severity: critical (every immutable value is mutable; a `Dict` can be
corrupted).**

`no_dunder_attribute` carves `__init__` out of the dunder ban, and its comment
says why: "`super().__init__(...)` is an `ast.Attribute` with a dunder attr,
and INFECTIONS.md allows `super` explicitly". The carve-out is on the *name*,
not on that syntax, so it applies to any receiver:

```bash
s = "abc"
s.__init__("zap")
s.print()            # -> zap        a str changed its value in place

n = 5
n.__init__(99)
n.print()            # -> 99

t = (1, 2)
t.__init__(9)
t.print()            # -> 9
```

and, keyed on one of those, a `Dict` ends up holding an entry reachable under
no key at all:

```bash
k = "a"
d = {}
d.at_put(k, 1)
k.__init__("b")
d.print()            # -> {'b': 1}
d.includes("a").print()   # -> False
d.includes("b").print()   # -> False
```

This is not a new hazard — it is the *same* one `Object._reject_dunder` already
describes, word for word: "`get_attr("__init__")` answered a callable that
re-initialized the receiver in place — `Str`, `Int` and `Tuple` all mutable,
and a `Dict` keyed on one left holding an entry reachable under neither the old
spelling nor the new." That fix passed `allow_init=False` on the `get_attr`
path and left the plain dotted spelling — the *shorter* one — untouched.

**Solution.** Narrow the carve-out from a name to the syntax it was written
for. `_Visitor.visit_Attribute` already has the receiver node in hand:

```python
def _is_super_call(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "super"
    )


class _Visitor(ErrorCollector):
    def visit_Attribute(self, node: ast.Attribute) -> None:
        message = dunder_message(node.attr, allow_init=_is_super_call(node.value))
        if message is not None:
            self.report(message, node)
        self.generic_visit(node)
```

`allow_init` already exists as a parameter — this is the third caller it was
built for. Verified on a patched build: all six programs above are refused at
validation time with the existing `.__init__ is forbidden — use Klass(...)
instead`, `super().__init__(...)` still parses and runs, and the full suite
passes unchanged (3439 tests, 100% coverage). No test and no example uses
`.__init__` on anything but `super()`.

`no_dunder_name`'s bare-`__init__` path is unaffected (`dotted=False` never
allowed it). `poop/validators/no_dunder_attribute.py`,
`tests/test_validators/test_no_dunder_attribute.py` (the four receivers above,
plus `super()` still allowed), and `INFECTIONS.md`'s dunder table, whose
`__init__` row should name the syntax rather than the dunder.

---

### 29. Every class-side message reports as `PoopMeta.<name>()`

**Severity: low (internal name in a user-facing diagnostic).**

`_cloak.py` exists because "CPython composes a *call-signature* error from the
**function's** `__qualname__` … so every wrong-arity message in the language
answered in POOP's internal vocabulary, names user code cannot even write".
`cloak` renames the functions in `vars(cls)`, unwrapping `classmethod` /
`staticmethod` through `__func__`. A `class_side` descriptor keeps its function
in `_fn`, and `PoopMeta` is never cloaked at all, so the class side — a
documented, user-facing surface — still answers the way instances used to:

```bash
class Foo(Object):
    pass

Foo.name(5)         # -> TypeError: PoopMeta.name() takes 1 positional argument but 2 were given
Foo.print(1, 2, 3)  # -> TypeError: PoopMeta.print() takes from 1 to 3 positional arguments ...
Foo.has_attr()      # -> TypeError: PoopMeta.has_attr() missing 1 required positional argument: 'name'
```

`PoopMeta` is a name a program cannot write, cannot reach (`_reject_private`
and the `_poop_*` mangling both hide the machinery), and will not find in any
documentation aimed at it.

**Solution.** Cloak the function when the descriptor is named, which is the one
moment it knows its own message name:

```python
    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name
        cloak_callable(self._fn, name)
```

`cloak_callable` is already the helper for exactly this case — a bare function
whose reported spelling must change without its binding changing — and it is
what makes `range(1, 2, 3, 4)` blame `range` instead of `_poop_range`. The
message then reads `print() takes from 1 to 3 positional arguments but 4 were
given`: no receiver, but no invented one either, and no internal name.

Answering `Foo.print()` instead would be better still and is not available
here — one function is shared by every class, and `__qualname__` is fixed when
the class body runs. Rewording inside `class_side.__get__` (the way
`Block.__call__` rewords a block's arity) would buy the receiver back at the
cost of a wrapper on every class-side send; not worth it for a diagnostic, but
worth recording as the alternative.

`poop/types/meta.py`, `poop/types/_cloak.py` (import only),
`tests/test_cloak.py`, whose existing sweep over instance methods is the
natural place for the class-side rows.

---

### 30. `pow` the message is narrower than `**` the operator and `pow` the builtin

**Severity: medium (the substitute refuses what the thing it replaces computes).**

`no_pow` forbids `pow(a, b)` and names `a.pow(b)`. `Int.pow` and `Float.pow`
call their own `__pow__` and turn a `NotImplemented` into a refusal — but
`__pow__` answers `NotImplemented` for a `Complex` *on purpose*, so that
CPython's operator protocol falls through to `Complex.__rpow__`. The operator
does exactly that; the message never gets there:

```bash
(2 ** complex(1, 1)).print()   # -> (1.5384778027279442+1.2779225526272695j)
(2).pow(complex(1, 1))         # -> TypeError: int does not understand #** with a complex
(2.0).pow(complex(1, 1))       # -> TypeError: float does not understand #** with a complex
```

CPython computes `pow(2, 1+1j)` too, so the substitute is narrower than the
builtin it replaces *and* than the operator POOP still allows — the same
expression answers a number one way and a refusal the other. The refusal is
also worded as an operator failure (`#** with a complex`) inside a method whose
name is `pow`.

`Complex` compounds it by having no `pow` at all: it defines `__pow__` and
`__rpow__`, and wraps `__abs__` and `__neg__` as `abs()` and `negated()`, but
the `pow` message that `Int` and `Float` both carry was never added.

```bash
(complex(1, 1) ** 2).print()   # -> 2j
complex(1, 1).pow(2)           # -> complex does not understand #pow
```

**Solution.** Two parts:

1. `Int.pow` / `Float.pow` must complete the protocol before refusing — try the
   reflected operation, which is what `**` does and what makes the deliberate
   `NotImplemented` meaningful:

   ```python
       def pow(self, other: object, modulus=None):
           result = self.__pow__(other, modulus)
           if result is NotImplemented:
               reflected = getattr(other, "__rpow__", None)
               if reflected is not None and _is_absent(modulus):
                   result = reflected(self)
           if result is NotImplemented:
               raise MIRRORS["TypeError"](binary_refusal("int", "pow", …))
   ```

   `modulus` is guarded because the three-argument form has no reflected
   counterpart in CPython either. The refusal's operator wording should become
   `pow` while it is being touched — `binary_refusal("int", "**", …)` names the
   operator inside the message named after the builtin.
2. Add `Complex.pow(other)` delegating to `__pow__` with the same
   NotImplemented handling, beside the existing `abs` and `negated`.

`Int.divmod` needs no change and must not get one: CPython refuses
`divmod(2, 1+1j)` too, so today's refusal is faithful.

`poop/types/int.py`, `poop/types/float.py`, `poop/types/complex.py`,
`tests/test_types/test_int.py`, `test_float.py`, `test_complex.py`,
`INFECTIONS.md`'s `pow` row.

---

### 31. `Bytes` and `ByteArray` do not answer `ord`

**Severity: low (a ban with no substitute on two receivers).**

`no_chr` forbids `ord(x)` and names `x.ord()`. CPython's `ord` takes a
one-character `str` **or** a one-byte `bytes`/`bytearray` — `ord(b"a")` is
`97` — and only `Str` answers the message:

```bash
"a".ord().print()          # -> 97
b"a".ord()                 # -> bytes does not understand #ord
bytearray(b"a").ord()      # -> bytearray does not understand #ord
```

**Solution.** Two three-line methods mirroring `Str.ord`, answering an `Int`
and letting CPython raise its faithful `TypeError` for a receiver that is not
exactly one byte long:

```python
    def ord(self) -> Int:
        return Int(ord(self._value))
```

`poop/types/bytes.py`, `poop/types/byte_array.py`, tests under
`tests/test_types/test_bytes.py` and `test_byte_array.py` (one byte, empty,
two bytes), and the `ord` row in `INFECTIONS.md`, which currently reads as if
`Str` were the only receiver.

---

### 32. The wording sweep is opt-in by program, so four more call-spellings survive

**Severity: medium (the guard against this whole family only covers a
hand-written list).**

`tests/test_no_python_wording.py` carries a pattern for "a message as a call"
(`\b\w+\(\)`) that would catch every leak below — but it runs only over
`_FAILING`, a hand-maintained list of programs. A leak survives simply by not
being on the list, which is how items 11, 12 and 18 accumulated, and these four
with them:

```bash
complex("abc")                 # -> ValueError: complex() arg is a malformed string
(-1).chr()                     # -> ValueError: chr() arg not in range(0x110000)
d = {"a": 1}
d.do(lambda p: d.at_put("b", 2))
                               # -> RuntimeError: dictionary changed size during iteration
```

The first two are CPython's, reaching a program through a POOP message. The
third is CPython's too, and adds a second problem: `dictionary` is not a word
POOP uses — the receiver prints as `dict` — and "during iteration" describes a
`for` loop the program did not write; it wrote `#do`.

Worse, POOP *authors* four of these itself, in messages raised through
`MIRRORS` — the mechanism that exists to make a diagnostic POOP's own:

```python
poop/transformers/complex.py:  "complex() argument must be int, float, str or complex, not …"
poop/transformers/complex.py:  "complex() first argument must be int or float, not …"
poop/transformers/complex.py:  "complex() second argument must be int or float, not …"
poop/transformers/int.py:      "int() can't convert non-string with explicit base"
```

The `int` one sits four lines below a docstring stating the rule it breaks:
"CPython answers `invalid literal for int() with base 10: 'abc'` — a Python
call". `int` and `float` were reworded to `'zz' is not a valid int`; `complex`
was left on CPython's phrasing throughout, in POOP's own voice.

**Solution.** Two parts, and the second is the one that matters.

1. Reword the six sites: `complex`'s three type refusals and its malformed
   string (`'abc' is not a valid complex`, mirroring `int`/`float`), `int`'s
   base refusal (`a base applies only to text`), `Int.chr`'s range refusal
   (`… is not a character code — codes run from 0 to 1114111`), and the
   mutation-during-iteration `RuntimeError`, caught where POOP iterates
   (`Dict.do`, the dict iterators) and reworded as `dict changed while it was
   being iterated — finish the iteration before adding or removing keys`.
2. Make the sweep exhaustive where it can be. The runtime half must stay a
   program list, but the *POOP-authored* half is statically checkable: walk
   `poop/` for every string literal passed to a `MIRRORS[...]` call and run the
   same `_FORBIDDEN` patterns over it. That catches a new `complex()` the day
   it is written, without anyone remembering to add a program — the same
   argument `tests/test_mirrored_raises.py` already makes for the *class* half
   of the rule ("per-site tests cannot stop the next wrapper from
   reintroducing it").

The static half needs one exemption list (a message may legitimately quote a
*POOP* selector like `#has_next`), which is the shape `_EXEMPT` in
`test_mirrored_raises.py` already uses.

`poop/transformers/complex.py`, `poop/transformers/int.py`,
`poop/types/int.py`, `poop/types/dict.py` and the dict iterators;
`tests/test_no_python_wording.py` (the four programs plus the static sweep).
