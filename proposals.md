# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

### 27. A block installed on a class is not bound to its receiver

`set_attr` on a class is sanctioned — item 2 refused it only for POOP's own
builtins, precisely so a program can extend the classes it defines — and the
one thing a reader would reach for it with does not work:

```
class C(Object): ...
C.set_attr("greet", lambda self: "hi")
C().greet()      # TypeError: block expects 1 argument, got 0
```

The receiver is never passed. A *zero*-argument block works
(`C.set_attr("greet", lambda: "hi")` answers `hi`), which says what is really
happening: the block is stored as a plain class attribute, and reading it
through an instance hands it back untouched. The refusal is the worst part —
the reader wrote a one-argument block and is told it got none.

Python's own rule is the one POOP wants here: a function found on the *class*
binds to the instance, a function found on the *instance* does not
(`C.greet = lambda self: 'hi'` then `C().greet()` answers `hi`; assigning the
same lambda to `c.greet` does not bind). POOP already agrees with the second
half by accident — `c.set_attr("greet", lambda: "hi")` works — and disagrees
with the first.

**Fix.** Give `Block` a `__get__` answering a block bound to the receiver, which
makes it a *non-data* descriptor and therefore reproduces Python's split
exactly: consulted for a class attribute, skipped for an instance one, no
special case needed. `Block` already wraps its lambda and already composes the
arity refusal, so the binding has one place to live. The half that works today
must keep working — a `Block` held as *state* (`self.callback = lambda: …`) is
data, not a method, and instance lookup never reaches the descriptor.

---

### 28. `Boolean` answers `to_bytes` and not `from_bytes`

`INFECTIONS.md` states the rule for this receiver: "A `Boolean` answers the
int-side messages too, not only the operators", and lists the family that was
re-supplied by hand because `bool` is an `int` in Python and POOP keeps them as
separate classes. One member of that family is missing, and it is half of a
pair whose other half is there:

```
True.to_bytes(1, "big")          # b'\x01'
True.from_bytes(b"\x01", "big")  # bool does not understand #from_bytes —
                                 #   did you mean #to_bytes?
```

CPython answers both (`bool.from_bytes` is `int.from_bytes`, inherited). The
hint makes it sharper than a plain gap: it points at the other half of the same
pair, so the reader is told the message they did not want is the one that
exists.

**Fix.** Delegate `from_bytes` through `_as_int`, as the rest of the int-side
family already does — it is a classmethod, so it answers an `Int`, which is
what CPython answers too (`bool.from_bytes(b"\x01", "big")` is `1`, not
`True`). The mechanical sweep that would have caught this is worth having as
well: for each wrapper, the public messages CPython's counterpart answers and
POOP's does not, with the deliberate omissions listed. It is how this was
found, and it reported exactly one other gap worth acting on (item 30).

---

### 29. `:explain subscript` teaches only half of what the validator says

`repl.py` explains a construct by running a snippet through the validators, and
says why out loud: "the explanation is the validator's own message, so the two
can never drift apart". They drifted anyway — not in wording, in coverage.
Item 18 gave `no_subscript` a second message for a *store*, and the snippet is
`x[0]`, a load:

```
>>> :explain subscript
subscript obj[key] is forbidden — use obj.at(key) instead
```

So the reader who wrote `xs[0] = 9`, was told to use `obj.at_put(key, value)`,
and typed `:explain subscript` to learn more is shown the *other* substitute —
the reading one, which is what item 18 exists to stop that reader from being
handed.

**Fix.** The snippet becomes both spellings (`x[0]` and `x[0] = 1`), and the
slice pair with them. `validate_all` already collects every error and
`_meta_explain` already prints them all, so a two-line snippet reports both
messages with no other change — verified. A test that each topic's snippet
reports *every* message its validator can compose would keep the coverage
honest, in the shape `test_doc_counts.py` uses for the README's numbers.

---

### 30. `MemoryView` is the one sequence that cannot be asked where

Every sequence in the family answers `index` and `count` — `List`, `Tuple`,
`Range`, `Bytes`, `ByteArray` — and `MemoryView` answers neither, though it
answers `at`, `len`, `slice`, `iter`, `includes` and `hex`, and CPython's
`memoryview` has had both since 3.10:

```
m = memoryview(b"aba")
m.includes(98)   # True
m.index(98)      # memoryview does not understand #index
```

`includes` is the substitute `no_in` names, so a program that has just been
told the element is there has no way to ask where. The gap is inside POOP
rather than against CPython: the surface criterion ("a message earns its place
when it substitutes a forbidden construct") does not admit `index` on its own,
but it admitted it on five siblings, and a reader moving between them meets one
receiver that answers differently.

**Fix.** Add both, delegating to the wrapped `memoryview` and routing the
failure through `_at.no_element_equal_to`, as `List.index` does — the sentence
is already written. The rest of what the surface sweep reported for
`MemoryView` (`cast`, `strides`, `suboffsets`, `nbytes`, `release`, …) is the
buffer protocol and stays out: it describes memory layout, which is the one
thing POOP has no vocabulary for.

---

### 31. A file its editor gave a BOM cannot be run

`poop/cli.py` reads the program with `encoding="utf-8"`, which keeps a
byte-order mark as a literal `U+FEFF` character in the source. CPython strips
it — running the same file with `python3` works — so POOP refuses a file
Python accepts, and refuses it in the tokenizer's vocabulary:

```
poop: invalid non-printable character U+FEFF (greet.py, line 1)
```

A reader has nothing to act on: the character is invisible in every editor, the
message names a code point rather than a byte-order mark, and nothing says the
file is fine and the *reading* of it is not. Editors on Windows write this mark
by default, so it costs a beginner their first program.

**Fix.** Read with `encoding="utf-8-sig"`, which strips a leading mark and is
otherwise identical to `utf-8` — the same thing CPython's own loader does. The
REPL's stdin path has it too (`printf '\xef\xbb\xbf…' | poop` answers the
same sentence) and takes the same one-word change wherever it decodes. A test
runs a source file with a mark on it, since nothing else in the suite reads
bytes that are not plain ASCII.

---

### ~~26. A subclass of an immutable builtin is born without its value~~ — DONE

**Decision + implemented.** `_endow` gives the alias the `__new__` step Python
has: one positional argument and no keywords is the shape every converter
takes, so it converts and the payload is written *before* `__init__` runs.

The residue the item predicted went the other way, and better. Rather than a
guard in `Object.__getattr__` answering after the fact, the split CPython
actually draws turned out to be available here too: a subclass with its own
signature gets the wrapper's **empty** value (`list.__new__` hands `__init__`
an empty list, so `class Pair(list)` with a two-argument constructor is an
ordinary empty list carrying its own state — CPython agrees), and where there
is no empty to give (an `int` has none) the object is refused at construction,
which is both where the mistake is and what CPython answers. So no message
ever reaches an unfinished object, and `__getattr__` was left alone.

One neighbour was found while covering the last branch and fixed with it:
`class Flag(bool)` was allowed at definition and failed at the first instance
with `Can't instantiate abstract class Flag without an implementation for
abstract methods '__bool__', '__str__', …` — a dozen dunders in one sentence
from a program that spelled none. `bool` is refused as a base now, where
CPython refuses it, and that made two branches in `__call__` dead code.

The full matrix — nine subclass patterns across the mutable and immutable
builtins — was run against CPython before and after, and agrees everywhere it
should; the one deliberate divergence (`super().__init__(v)` on an `int`
subclass, a `TypeError` in CPython) is argued in the item above.
`poop/types/_alias.py`, `tests/test_transformers/test_type_names.py`,
`INFECTIONS.md`.

---

### ~~22. A class-side constructor breaks under the name a program writes~~ — DONE

**Decision + implemented.** `fromhex` and `from_bytes` built through `cls`, and
`cls` is whatever the program named — under a bare builtin name that is the
alias, whose call is the *converter*, which takes what a program writes rather
than the finished Python value a classmethod holds. So all three broke in the
only spelling a reader would use while the instance form quietly worked.

`_alias.wrapped_instance` answers the three receivers: the alias answers the
wrapper's own instance, a plain wrapper builds itself, and a program's
`class B(bytes)` is built from the wrapper's constructor, so `B.fromhex(…)`
still answers a `B` — the case that ruled out the simpler `unalias(cls)(…)`.
`ByteArray.fromhex` was added alongside: `Bytes` and `ByteArray` mirror each
other message for message and this was the one half-pair, for a spelling
CPython supports. `poop/types/_alias.py`, `poop/types/{bytes,byte_array,int,
float}.py`, four test modules, `INFECTIONS.md`.

---

### ~~23. `super().__init__(...)` is the third home of the convert/build gap~~ — DONE

**Decision + implemented.** The alias carries its own `__init__`, which
converts and fills the payload. The MRO puts it exactly where `super()` looks —
`S.__mro__` is `(S, <alias>, List, …)` — so it intercepts that call and nothing
else, and the three spellings of one intent (`list(xs)`, `Sub(xs)`,
`super().__init__(xs)`) now agree.

One consequence is deliberate and worth recording: `super().__init__(*xs)`, the
spelling that used to be the workaround, now answers `list is built from at
most one collection, got 2 arguments` — which is what the direct call answers,
and what CPython answers to `list.__init__(self, 1, 2)`. A program written
against the bug changes behaviour; a program written against Python does not.
`poop/types/_alias.py`, `tests/test_transformers/test_type_names.py`,
`INFECTIONS.md`.

---

### ~~24. `Str.format` is POOP's template surface with CPython's failures~~ — DONE

**Decision + implemented.** All five modes are worded now: a missing name says
what the template asked for and which arguments it was given, a missing
position counts the values it got, and a spec the value cannot take names the
value's kind. The brace errors keep the parser's sentence with `format string`
replaced by `template`, since the fault they report really is in the text.

Two things fell out of writing it. `_reject_field_access` had to move *inside*
the guard — the unmatched-brace errors are raised by the parser it runs, not by
`format` — and its own refusal therefore has to pass through untouched, on the
`PoopExcMeta` test `reword_if_native` uses for exactly that reason. The five
programs joined `_FAILING`, which is where the bare `KeyError: 'a'` is pinned:
the sweep's "still says something" half catches a one-word message, while the
patterns did not, and the exact wording is pinned in `tests/test_types/test_str.py`.
`poop/types/string.py`, `tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~25. `int.superclass()` answers a class that calls itself `int`~~ — DONE

**Decision + implemented.** `PoopMeta.superclass` skips a base that `unalias`
maps to the receiver, so the ladder no longer has a rung that is not there:
`int.superclass()` answers `object`, one step, and the answer is the same class
`(5).class_().superclass()` gives. It is the same "the alias and its wrapper
are one class" decision item 12 made for `==`, which makes this the third
question `_alias.unalias` answers. A program's own `class Stack(list)` is
unaffected — its superclass *is* `list`, the name it wrote. `poop/types/meta.py`,
`tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~12. A class comparison answers a Python `bool`, and answers it wrongly~~ — DONE

**Decision + implemented.** `PoopMeta` defined no `__eq__`, so `int == int`
fell through to `type.__eq__` and handed a raw Python `bool` to user code,
which answered `'bool' object has no attribute 'print'` — CPython's word for
the thing POOP calls a message, from the shortest program that compares two
classes. `__eq__` / `__ne__` answer a `Boolean` now and read both sides
through `unalias`, which closes the silent half too: `(5).class_() == int` was
`False` about two objects that both call themselves `int`.

`is_identical` deliberately does *not* unalias — it asks identity, and those
really are two objects — so the pair disagrees by design, and `INFECTIONS.md`
says which one a reader comparing classes should send. `__hash__` is
re-declared as `type.__hash__`, since defining `__eq__` drops it and
`NATIVE_TO_POOP` keys on classes. `poop/types/meta.py`,
`tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~13. A builtin subclass constructs by the wrapper's rules, not the converter's~~ — DONE

**Decision + implemented.** `_AliasMeta.__call__` read `_converter` off
`cls.__dict__` and stopped there, so the convert-versus-build gap item 9
closed stayed open one level down — for the spelling `_alias.py` itself calls
a legal use of a bare name. The converter is looked up along the MRO now and
its answer rebuilt as `cls`, slot by slot: a subclass has the wrapper's slots,
and `_payload_slots` reads them off `__slots__` rather than a table, so a new
wrapper is covered by having one. The payload is copied, since a converter may
answer a value it was handed.

Two exceptions, both deliberate. A subclass declaring its own `__init__` is
built by it — that is what the `__dict__` read was protecting. And `bool` is
not rebuildable: its two values are singletons with no payload, so its
converter's answer passes through, which is why the mechanical test's table
has twelve rows and not thirteen. `poop/types/_alias.py`,
`tests/test_transformers/test_type_names.py`, `INFECTIONS.md`.

---

### ~~14. `encode` / `decode` do not guard the encoding argument~~ — DONE

**Decision + implemented.** The codec table is read by lowercasing the
argument, so `"ab".encode(1)` answered `'int' object has no attribute 'lower'`
— the wrapper naming the Python method it happens to call, the shape item 10
closed everywhere else. Both arguments pass `_argument.text_like` before the
lookup, and the handler stops reporting a wrong-*typed* argument as a
wrong-*valued* one.

`text_like` grew a `kinds` parameter for the two callers that mean `str` and
nothing else; narrowing it fixes `byte_order` the same way, where `b"big"`
used to slip past the type check and fail as a value. `poop/types/_codec.py`,
`poop/types/_argument.py`, three wrappers, `tests/test_types/test_codec.py`,
`INFECTIONS.md`.

---

### ~~15. A `Set` refuses a set argument that Python accepts~~ — DONE

**Decision + implemented.** `s.includes({1})`, `s.discard({1})` and
`s.remove({1})` all answered `cannot use 'set' as a set element` — a refusal
about *storing*, given to three messages that only look. `_set_algebra.probed`
answers a mutable set operand with an equivalent `FrozenSet`, which hashes and
compares exactly as a stored one does, so a set really held inside a set is
found rather than blanket-refused, `remove` reaches POOP's own
`no_element_equal_to`, and `add` still refuses. Recognised through the
`_set_like` marker `_other_set` already used, so no `Set` ↔ `FrozenSet` import
cycle. `poop/types/_set_algebra.py`, `poop/types/{set,frozen_set}.py`, both
test modules, `INFECTIONS.md`.

---

### ~~16. The exception hierarchy misses what POOP's own surface raises~~ — DONE

**Decision + implemented, and the two halves went different ways.** `EOFError`
is mirrored: `Str.input` is the only message that reads from outside the
program, end of input needs nothing more exotic than a pipe — it is what
`examples/basics/greet.py` answered `EOF when reading a line` to — and without
a mirror the class could not be named at all, while `except_(Exception, …)`
reported the kind as `Exception`. `input` raises it with a sentence of its own.

The `Unicode*` family is **not** mirrored, against what this item proposed.
Its constructor takes five arguments and its `__str__` composes them into the
`codec` sentence `_codec.py` exists to keep out, so a mirror would have
reproduced the very message that made this a bug; and `poop_class_of` already
answered `ValueError` for it, which is what `UnicodeError` is in CPython's own
tree. Both failures are reworded instead — `ascii cannot encode 'é' at
position 1`, `utf-8 cannot decode byte 0xff at position 0` — under one class a
program can spell, which also ends the disagreement between the uncaught
report and the handler. `poop/types/exceptions.py`, `poop/types/_codec.py`,
`poop/types/string.py`, three test modules, `INFECTIONS.md`.

---

### ~~17. The mutation refusal names the receiver in `do` and hides it in `next`~~ — DONE

**Decision + implemented.** `_mutated.iterating` exists so the refusal names
its receiver, and the cursor passed the literal `"the collection"` — so
`d.do(…)` and `d.iter().next()` reported one fact in two vocabularies, with
the anonymous half being the protocol `_peek.py` holds up as idiomatic.

The label is derived from the CPython iterator name each concrete iterator
already declares (`list_iterator` → `list`), so a new iterator cannot ship
without one; `iterating=` covers `memory_iterator`, the single name whose
prefix is not the collection's own spelling. The lazy views keep the default,
which is honest rather than wrong — they cannot name the collection behind
them. `poop/types/_peek.py`, `poop/types/_iterator_base.py`,
`poop/types/memory_view_iterator.py`, `tests/test_types/test_peek.py`,
`INFECTIONS.md`.

---

### ~~18. `no_subscript` names a reader as the substitute for a write~~ — DONE

**Decision + implemented, in two commits.** `List.at_put` first, because a
validator may not refuse a construct with no substitute to name: `Dict` and
`ByteArray` both answered `at_put` and the collection between them — indexable,
mutable, ordered — could not replace an element at all. It mirrors
`ByteArray`'s down to both refusals and answers the receiver, so a write
chains.

Then the validator reads the context off the node: an `ast.Store` (augmented
assignment included) names `obj.at_put(key, value)`, a `Load` still names
`obj.at(key)`. The slice branch splits the same way but has no whole-slice
substitute to point at, so it says what can be done — element at a time —
rather than naming `slice`, which reads. `poop/types/list.py`,
`poop/validators/no_subscript.py`, `tests/test_types/test_list.py`,
`tests/test_interpreter.py`, `INFECTIONS.md`.

---

### ~~19. `Dict.do` disagrees with every other way of iterating a `Dict`~~ — DONE

**Decision + implemented.** The override is dropped rather than rewritten: the
mixin's `do` walks `__iter__` like `map`, `filter`, `sorted`, `min`, `max` and
`iter` already did, and carries the same mutation guard worded from the
receiver, so deleting eight lines was the whole change. `d.items().do(…)` is
the pair spelling and answers `Tuple`s already.

Breaking, as the item said — a block written for the pair form now receives the
key. The sweep found nothing to change: no example iterated a `Dict` with `do`.
`poop/types/dict.py`, `tests/test_types/test_dict.py`, `INFECTIONS.md`.

---

### ~~20. `With` hands `__exit__` three raw Python values~~ — DONE

**Decision + implemented.** `__exit__` now receives what `Try` hands a
handler — `poop_class_of(e)`, `Error(e)` — and `none` for the traceback, on
both paths. The class docstring already called the *protocol* the deliberate
primitive leak; the values were never part of that argument, and the third one
was an introspection surface reached through a dunder no program may spell.
The three-argument shape is unchanged, so a manager written to Python's
signature still binds.

`examples/idiomatic/managed_resource.py` came in a second commit: `With` had no
example at all, and it is the one construct where a POOP program implements
dunders itself. `poop/types/with_.py`, `tests/test_types/test_with_.py`,
`examples/`, `README.md`, `INFECTIONS.md`.

---

### ~~21. A user class cannot satisfy the protocol slots it is allowed to define~~ — DONE

**Decision + implemented.** `PoopMeta.__new__` unwraps the answer of a
user-defined `__str__`, `__repr__`, `__bool__`, `__hash__` or `__len__` where
the class is built. A native answer short-circuits, which is what keeps the
wrappers in `poop/types/` untouched and the package importable at all —
`bool(x)` runs during its own import, before `_bridge` can be loaded.

A wrong answer is refused by the *role* (`P's text must be a str, got an int`),
never by the slot: a message spelling `__str__` would name the construct
`no_dunder_attribute` bans, which is exactly what made CPython's own sentence
unreadable (`__str__ returned non-string (type str)` calls `str` the thing
that is not a `str`). `__len__` was the quiet member — it raised nothing and
did nothing — so a class declaring it and no `len` now answers that message
too. `poop/types/meta.py`, `tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~1. The exception mirrors and `Ellipsis` can be shadowed silently~~ — DONE

**Decision + implemented.** `no_builtin_shadow` reserved the 17 lowercase
builtins and both spellings of the root, and not the 16 `MIRRORS` names
`ExceptionTransformer` rewrites the same way, nor `Ellipsis`. Both sides of the
hazard its own docstring describes for `dict` were live: an assignment target
*is* an `ast.Name`, so `ValueError = 5` clobbered the mirror globally, while a
parameter (`ast.arg`) and a class name (`ClassDef.name`) are not — they kept
their spelling while every read of them in the body still resolved to the
mirror, so `def hold(self, ValueError): return ValueError` answered the class
and never saw its argument. `Ellipsis` was the sharpest, being the named
spelling of a *literal*: after `Ellipsis = 5`, `...` itself answered `5`.

The mirror half of the reserved set is derived from `MIRRORS` rather than
tabulated, for the reason `no_namespace_shadow` reads `DEFAULT_NAMESPACE` — a
seventeenth mirror cannot be added without the reservation following it. The
legal neighbours still run: `ValueError.raise_(…)`, `class MyErr(ValueError)`,
and a method named after a mirror (which binds as a class attribute).
`poop/validators/no_builtin_shadow.py`,
`tests/test_validators/test_no_builtin_shadow.py`, `INFECTIONS.md`.

---

### ~~2. The class side lets a program rewrite POOP's own builtin classes~~ — DONE

**Decision + implemented.** `__slots__` keeps state off the instance side and
`Object.set_attr` has a sentence for that refusal; the class side had no
equivalent, and `class_()` hands the class out — so
`"abc".class_().del_attr("upper")` removed `upper` from every string in the
program, and `(5).class_().set_attr("bit_length", block)` replaced a message on
`int`. The only names that happened to be safe were the `class_side`
descriptors, whose `__set__` refuses.

A new `_reject_builtin(cls)` in `poop/types/meta.py` refuses a write to a class
the program did not define, keyed on `__module__`: `cloak` puts every wrapper
and mirror in `builtins`, while a class a POOP program defines carries
`__poop__`. It cannot be forged — `__module__` is a dunder, so
`no_dunder_attribute` refuses the literal spelling and `_reject_dunder` the
computed one. The name is checked *before* the receiver, so a forbidden name
still answers the ban it broke. `tests/test_types/test_meta.py`, `INFECTIONS.md`.

---

### ~~3. `Object.del_attr` has no refusal of its own~~ — DONE

**Decision + implemented.** `set_attr` caught CPython's `AttributeError` and
composed POOP's sentence; `del_attr`, three lines below in the same
four-message family, did not — so `"abc".del_attr("zzz")` answered `'str'
object has no attribute 'zzz' and no __dict__ for setting new attributes`,
naming the dunder `_reject_dunder` will not even let a program spell.

Two branches rather than one, because the two failures are different facts: an
object that *can* hold state simply does not hold this name (`C has no
attribute 'b' to remove`), and telling a user class it "holds no state of its
own" would be false. `set_attr` needs only one, since a receiver with a
`__dict__` never fails there. Both programs joined `_FAILING`.
`poop/types/object.py`, `tests/test_types/test_object.py`,
`tests/test_no_python_wording.py`.

---

### ~~4. `Str.format` cannot apply a format spec to a `Complex`~~ — DONE

**Decision + implemented.** `_bridge.to_python` unwrapped every scalar rung
except `Complex`, so a complex reached `str.format` still wrapped and any real
spec hit `object.__format__`: `"{:.2f}".format(complex(1, 2))` failed where
CPython answers `1.00+2.00j`, and named `complex.__format__` on the way out.
`Complex` joined the scalar branch, and `to_poop` grew the mirror branch — the
two halves are documented as a pair, and a one-sided bridge is the next
reader's trap. `poop/types/_bridge.py`, `tests/test_types/test_bridge.py`.

---

### ~~5. `has_next` leaks CPython's `dictionary changed size during iteration`~~ — DONE

**Decision + implemented.** `next` and `__next__` reworded the mutation
refusal and `has_next` — the one message of the three that exists so a program
can *ask* instead of raising — read straight from CPython. It carries the same
`reword_if_native` guard now, and POOP's own `RuntimeError`s still pass through
untouched. The program joined `_FAILING`, which is what would have caught it:
the sweep was opt-in *by program* and none exercised `has_next`.
`poop/types/_peek.py`, `tests/test_types/test_peek.py`,
`tests/test_no_python_wording.py`.

---

### ~~6. `Str.rfind` / `Str.rindex` do not guard the needle~~ — DONE

**Decision + implemented.** `_needle` was wired into `find`, `index` and
`count` and not into their `r`-prefixed twins, which are the same message read
from the other end — so `"abc".find(block)` and `"abc".rfind(block)`, the same
mistake one letter apart, answered in two different vocabularies. Both route
through `_needle` now, and `_needle` itself grew the non-block case (item 10's
`find() argument 1 must be str, not int`). `poop/types/string.py`,
`tests/test_types/test_str.py`, `tests/test_no_python_wording.py`.

---

### ~~7. `Boolean` refuses every non-empty format spec~~ — DONE

**Decision + implemented.** A `Boolean` has no `_value` slot, so
`Object.format` fell through to `object.__format__`, which accepts only the
empty spec — `True.format(">6")` refused while `"{:>6}".format(True)`, routed
through `to_python`, answered `'     1'`. The override folds to the Python
`bool`, **not** through `_as_int`: `format(True, "")` is `'True'` and
`format(1, "")` is `'1'`, so folding first would have changed
`True.format()` — the one spelling that already worked. `poop/types/boolean.py`,
`tests/test_types/test_boolean.py`.

---

### ~~8. `pow`'s modulus is refused in two different vocabularies~~ — DONE

**Decision + implemented.** Two commits' worth of one concern. `Int.__pow__`
composed POOP's sentence for two of the three ways a modulus can be wrong and
left the third to CPython's `pow() 3rd argument cannot be 0` — the builtin
`no_pow` forbids, spelt as the call. And `Float.pow` had no `modulus`
parameter at all, so `(2.0).pow(3, 5)` answered CPython's *signature* error
while `(2).pow(3.0, 5)` one line away answered the operation.

`Float.pow` grew the third slot and refuses it as an operation, reusing `Int`'s
wording so the tower answers one thing; the guard lives in `pow`, not
`__pow__`, because the operator never carries a third operand. `Boolean.pow`
picked both up for free through `_as_int`. `poop/types/int.py`,
`poop/types/float.py`, `tests/test_types/test_int.py`,
`tests/test_types/test_float.py`, `tests/test_no_python_wording.py`.

---

### ~~9. An aliased constructor is a different constructor~~ — DONE

**Decision + implemented.** Every converter transformer has two rewrites —
`visit_Call` to the converter, `visit_Name` to the wrapper *class* — and the
two mean different things. `_arity.py` closed exactly that gap for the direct
call; binding the name first reopened it one indirection away, and mostly in
silence: `x = list; x([1, 2])` answered `[[1, 2]]`, `x = tuple; x([1, 2])`
answered `([1, 2],)`, and `x = int; x(4.9)` answered an `int` **holding 4.9**,
which then said `float does not understand #+ with an int`.

The metaclass-dispatch shape the proposal recommended needed one refinement:
the wrapper classes cannot dispatch, because `poop/types/` builds its values by
calling them directly and that is the other meaning. So each bare name binds a
`_poop_<name>_cls` **alias** instead (`poop/types/_alias.py`) — a subclass of
the wrapper whose metaclass answers a *call* with the converter, guarded on
`cls.__dict__` so `class Stack(list)` still constructs a `Stack`. It stays a
class because that is what a bare name is otherwise for:
`(5).is_instance(int)`, `class Stack(list)`, `int.name()`.

One thing worth recording, because it looks like the obvious move: an
`__instancecheck__` delegating to the wrapped class — the shape `PoopExcMeta`
uses for the mirrors — cannot work here. The alias *is* a subclass, so
`ABCMeta`'s subclass walk reaches it and asks the same question, recursing
until the stack gives out. The type-argument case is answered one level up
instead, by `unalias`, which both `is_instance`/`is_subclass` pairs call.
`slice` needs no alias: it has no converter, and `Slice(start, stop, step)`
already *is* the call.

All 17 aliased constructors now answer what their direct spelling answers, and
the mechanical test the proposal asked for pins every row.
`poop/types/_alias.py`, 16 transformer modules, `poop/types/object.py`,
`poop/types/meta.py`, `tests/test_transformers/test_type_names.py`,
`INFECTIONS.md`.

---

### ~~10. The wording sweep is opt-in by program, and 47 leaks are hiding behind that~~ — DONE

**Decision + implemented.** The structural half first: a third half of
`tests/test_no_python_wording.py` now sends every public message on every
wrapper with wrong-typed arguments and runs `_FORBIDDEN` over what comes back,
with CPython's wrong-arity shape exempt (`_cloak`'s docstring says out loud
that it only renames the callee). It reported 83 leaks on the tree as it stood
— more than the 47 the proposal measured, because the proposal had already
folded some into items 3, 6 and 7.

All of them are closed. The refusals live in a new `poop/types/_argument.py` —
`a_class`, `a_bound`, `text_like`, `byte_order` — one guard per argument
*kind* rather than one per receiver, which is what makes the same sentence read
the same on `Str`, `Bytes` and `ByteArray`:

- `isinstance() arg 2 must be a type` from `x.is_instance(…)` — the banned
  builtin spelt as the call replacing it, on all 15 receivers at once.
- `slice indices must be integers or None or have an __index__ method` from the
  `start`/`end` of `find`/`rfind`/`index`/`rindex`/`count`/`startswith`/
  `endswith` on the three text wrappers, plus `list`/`tuple`'s `index`.
- Both halves of `Object.format`: a non-`Str` spec (`format() argument 2 must
  be str`) and a receiver with no `_value` (`unsupported format string passed
  to list.__format__`).
- The `<msg>() argument N must be …` family across a dozen text arguments, the
  `to_bytes`/`from_bytes` byteorder, `fromhex`, `hex`'s separator, and
  `ByteArray.at_put`'s index.

Two behaviour changes fell out and are deliberate: `hex(<not text>)` is now a
`TypeError` rather than the `ValueError` CPython reaches by measuring the
length of a non-separator, and `byte_order` splits the two failures the way
CPython classes them — a non-string is a `TypeError` about the argument's kind,
a misspelt one a `ValueError` about its value. `poop/types/_argument.py`,
`poop/types/{object,meta,boolean,string,bytes,byte_array,int,list,tuple}.py`,
`tests/test_no_python_wording.py`, `INFECTIONS.md`.

---

### ~~11. Three counts in the docs have drifted past the code~~ — DONE

**Decision + implemented.** `CLAUDE.md` said 69 validators, `README.md` said
~69 and 41 example programs, against 70 and 43. All three corrected — and
because every one of them is derivable, a new `tests/test_doc_counts.py` reads
the numbers *out of the Markdown* and compares them against the live
registries. A test asserting `len(DEFAULT_VALIDATORS) == 70` would only have
moved the problem to a fourth place to keep in step; this makes the drift
unrepresentable, and it also pins the README's bullet list against the files on
disk — the list was right while the sentence above it was two behind, which is
what made the drift invisible to a reader skimming either one. `CLAUDE.md`,
`README.md`, `tests/test_doc_counts.py`.
