# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

### 12. A class comparison answers a Python `bool`, and answers it wrongly

Two facts, one cause. `Object.__eq__` answers a `Boolean`, so `(5 == 5)` is a
POOP object — but a *class* is compared by its metaclass, and `PoopMeta` defines
no `__eq__`. So the comparison falls through to `type.__eq__` and a raw Python
`bool` reaches user code:

```
(int == int).print()
#  ->  AttributeError: 'bool' object has no attribute 'print'
```

The failure names `'bool' object` and an *attribute*, which is CPython's
vocabulary for the thing POOP calls a message, and it is reached by the shortest
program that compares two classes. `!=` leaks the same way, and so does any
`.if_true(...)` / `.not_()` a program would send next.

The second fact is worse because it is silent. `class_()` answers the wrapper,
while a bare builtin name answers the `_alias.py` subclass of that wrapper
(item 9), so the two are different objects with the same `name()`:

```
(5).class_().name().print()  # int
int.name().print()  # int
(5).is_instance(int).print()  # True
(5).class_().is_identical(int).print()  # False   <-- both are "int"
```

`is_instance` is right because both pairs route through `unalias`; the equality
a reader reaches for first does not, and answers `False` for a program that is
correct.

**Fix.** Give `PoopMeta` an `__eq__` / `__ne__` answering a `Boolean`, comparing
`unalias(cls)` against `unalias(other)` so a wrapper and its alias are one
class — which closes both halves at once — and keep `__hash__` explicitly
(defining `__eq__` drops it, and `NATIVE_TO_POOP` keys on classes). `unalias`
already lives in `poop/types/_alias.py` and is already what
`is_instance`/`is_subclass` call, so this is the same answer given to a third
question rather than a new rule. `is_identical` must *not* follow it — it is
identity, and a wrapper and its alias really are two objects — so the pair will
disagree by design, and `INFECTIONS.md` should say which of the two a reader
comparing classes is meant to send.

---

### 13. A builtin subclass constructs by the wrapper's rules, not the converter's

Item 9 closed the gap between "convert this value" and "build from these
elements" for a bare name. `_AliasMeta.__call__` reads `_converter` from
`cls.__dict__` rather than inheriting it, deliberately — "a subclass must behave
normally, or `class Stack(list)` would answer a `List` from `Stack()`" — and
that leaves the whole gap open one level down, for the exact spelling
`_alias.py` names as a legal use of a bare name (`class Stack(list): ...`):

```
class Stack(list): ...
Stack([1, 2]).len().print()   # 1   — a Stack holding one list
list([1, 2]).len().print()    # 2

class N(int): ...
n = N(4.9)                    # an int holding 4.9, exactly item 9's example
(n + 1)                       # float does not understand #+ with an int

class D(dict): ...
D({"a": 1})                   # TypeError: dict.__init__() takes 1 positional
                              #            argument but 2 were given
class S(str): ...
S(5)                          # TypeError: __str__ returned non-string (type int)

class T(set): ...
T([1, 2])                     # TypeError: cannot use 'list' as a set element
```

It is not a handful of them. Sending `class Sub(<name>): ...` the argument its
converter takes, and comparing `Sub(x).repr()` against `<name>(x).repr()`, every
row disagrees:

```
              Sub(x)                          <name>(x)
int(4.9)      4.9                             4
float("2.5")  2.5  (holding the str)          2.5
str(5)        5    (holding the int)          '5'
bytes("ab")   'ab' (holding the str)          b'ab'
list([1, 2])  [[1, 2]]                        [1, 2]
tuple([1,2])  ([1, 2],)                       (1, 2)
complex(…)    '1+2j' (holding the str)        (1+2j)
bool(1)       TypeError: Sub() takes no arguments
bytearray(…)  TypeError: 'str' object cannot be interpreted as an integer
dict({…})     TypeError: dict.__init__() takes 1 positional argument but 2 …
set([1, 2])   TypeError: cannot use 'list' as a set element
frozenset(…)  the same
range(3)      TypeError: range.__init__() missing 1 required positional …
```

Seven are silent — "a value whose class and contents disagree", as item 9 put
it, and each one detonates at the next message (`N(4.9) + 1` answers `float
does not understand #+ with an int`). Six refuse, and every refusal is a Python
one: a dunder, an arity, or a slot name, which is what items 3 and 10 exist to
prevent.

**Fix.** Route a subclass through the converter too, then build `cls` from the
result — `_AliasMeta.__call__` looks `_converter` up along the MRO, and when
`cls` is not the alias itself it converts the arguments and constructs `cls`
from the converted payload. The guard that must survive is the one the current
`__dict__` read was protecting: a subclass defining its own `__init__` keeps it,
and `Stack()` answers a `Stack`, not a `List`. The mechanical test of item 9
(`tests/test_transformers/test_type_names.py`) should grow a second row per
constructor: `class Sub(<name>)` answers what `<name>(...)` answers, with the
subclass's own class.

---

### 14. `encode` / `decode` do not guard the encoding argument

`poop/types/_codec.py` exists so the codec table never shows through: it names
four encodings and three handlers and refuses the rest in POOP's words. Both
entry points hand the argument to `encoding_name`, which calls `.lower()` on it
before anything checks what it is:

```
"ab".encode(1)  #  AttributeError: 'int' object has no attribute 'lower'
b"ab".decode(1)  #  the same, from ByteArray too
```

That is an internal implementation detail read back to the user — the wrapper
naming the Python method it happens to call — and it is the shape item 10
closed everywhere else with `poop/types/_argument.py`. The handler argument is
half-guarded in the other direction: `"ab".encode("utf-8", 1)` answers
`unknown error handler 1 — POOP handles strict, ignore and replace`, a
`ValueError` about a *value* for what is a wrong-typed argument, the split item
10 settled for `byte_order` (a non-string is a `TypeError` about the argument's
kind, a misspelt one a `ValueError` about its value).

**Fix.** Send both arguments through `_argument.text_like` before the lookup, so
a non-`Str` answers `encode() argument 'encoding' must be str` in POOP's voice
and only a real string reaches `encoding_name` / `handler_name`. One guard in
`_codec.py` covers `Str.encode`, `Bytes.decode` and `ByteArray.decode` at once,
which is the reason `_argument.py` is keyed on argument *kind*.

---

### 15. A `Set` refuses a set argument that Python accepts

CPython's `set.discard`, `set.remove` and `in` accept an unhashable `set`
argument on purpose — they probe with a temporary `frozenset`, so asking
whether a set is inside a set is an ordinary question with an ordinary answer.
POOP refuses all three:

```
s = {1, 2}
s.discard({1})  # TypeError: cannot use 'set' as a set element
s.includes({1})  # TypeError: … (CPython answers False)
s.remove({1})  # TypeError: … (CPython answers a KeyError)
```

A `FrozenSet` argument works, so the divergence is invisible until a program
holds a `Set`. `remove` is the sharpest of the three: the refusal it should
answer is `no_element_equal_to`, POOP's own sentence, and it never gets there.

**Fix.** In `Set` / `FrozenSet`'s `discard`, `remove`, `includes` and
`__contains__`, convert a `Set` argument to the equivalent `FrozenSet` payload
before probing `_data`, mirroring CPython's fallback. The probe is
read-only, so no element is ever stored — the ban on a `Set` *inside* a set
(`{1}.add({2})`) stays exactly as it is, which is the distinction CPython draws
and POOP currently does not.

---

### 16. The exception hierarchy misses what POOP's own surface raises

`poop/types/exceptions.py` justifies its 16 mirrors with a reachability
argument: "a language with no I/O and no codecs cannot reach the `OSError`
subtree or the `Unicode*` family". POOP has one input message and four
encodings, and both of those are reachable through them:

```
"héllo".encode("ascii")
#  ->  UnicodeEncodeError: 'ascii' codec can't encode character '\xe9'
#      in position 1: ordinal not in range(128)
```

The sentence advertises a `codec` — the word `_codec.py` was written to keep out
of messages — under a class name no program can spell. `EOFError` is the same
gap on the input side, and it is not hypothetical: `examples/basics/greet.py`,
a shipped example, answers `EOFError: EOF when reading a line` the moment its
stdin is a pipe rather than a terminal, and no program can catch it by name:

```
Try(lambda: "name? ".input()).except_(EOFError, handler).run()
#  ->  NameError: name 'EOFError' is not defined
```

`except_(Exception, …)` does catch it, but `e.kind().name()` then answers
`Exception` — `poop_class_of` walks to the nearest mirrored ancestor, which is
right as a rule and lossy exactly here, so the uncaught path prints
`UnicodeEncodeError` while a handler is told `ValueError`: one exception, two
names.

**Fix.** Add the three natives POOP's own surface can raise to `_HIERARCHY` —
`EOFError` under `Exception`, `UnicodeEncodeError` and `UnicodeDecodeError`
under `ValueError` (their real parent) — and reword the two messages the way
every other reachable failure is worded: `input`'s EOF as end of input rather
than "EOF when reading a line", and the codec failures as the character and
position that could not be encoded, without naming a codec module. Mirroring is
the cheap half; the docstring's reachability argument should be corrected in the
same commit, since it is what will be read the next time someone asks whether a
mirror is needed.

---

### 17. The mutation refusal names the receiver in `do` and hides it in `next`

`_mutated.py` carries `iterating(receiver)` — "the label for a receiver being
iterated — its own cloaked name" — and two call sites use it. The three sites in
`_peek.py` pass the literal `"the collection"` instead, so the same fact reads
two ways depending on which message noticed it:

```
d = {"a": 1}
d.do(lambda k: d.at_put("b", 2))
#  ->  dict changed while it was being iterated — …

d = {"a": 1}
it = d.iter()
d.at_put("b", 2)
it.next()
#  ->  the collection changed while it was being iterated — …
```

This is the shape items 6 and 8 closed: one operation answering in two
vocabularies because the guard was wired into one spelling and not its twin.
Here the anonymous half is the *cursor* protocol `_peek.py`'s own docstring
calls the idiomatic one, so it is the wording a reader following the examples
meets first.

**Fix.** Give `_PeekMixin` the label of the collection it iterates — the
concrete iterators already hold it (`ListIterator` is built from the list's
items) — and pass it to `reword_if_native` in `has_next`, `next` and `__next__`,
so `d.iter().next()` says `dict` for the same reason `d.do(…)` does. A default
of `"the collection"` keeps an iterator that cannot name its source honest
rather than wrong.

---

### 18. `no_subscript` names a reader as the substitute for a write

`obj[key] = value` is refused with the substitute for *reading*:

```
xs = [1, 2]
xs[0] = 9        # subscript obj[key] is forbidden — use obj.at(key) instead
xs.at_put(0, 9)  # list does not understand #at_put

d = {}
d["a"] = 1       # subscript obj[key] is forbidden — use obj.at(key) instead
d.at_put("a", 1) # works — the message just never mentions it
```

Two problems, one line apart. For a `Dict` the substitute exists and the
refusal names the wrong one, so a reader follows the advice, writes
`d.at("a")`, and gets a `KeyError` for a program that was trying to *store*.
For a `List` there is no substitute at all: `at_put` is defined on `Dict` and
`ByteArray` — `INFECTIONS.md` lists both as "POOP-specific methods with no
Python equivalent" — and not on the one collection between them that is
indexable, mutable and ordered. `xs.append`, `xs.insert` and `xs.pop` can
simulate it (`xs.pop(i)` then `xs.insert(i, v)`), which is a two-message dance
for one assignment and changes the list in between.

This is the rule `CONTRIBUTING.md` states for validators: "Activate a validator
only when the substitute exists — blocking without offering an alternative
breaks code without teaching." `no_subscript` is active for the store context
with no substitute for the most ordinary receiver.

**Fix.** Two commits. Add `List.at_put(index, value)`, mirroring `ByteArray`'s
(same name, same `Index` guard, same `self` return for chaining), so the
substitute exists. Then let `no_subscript` see the context it is refusing — an
`ast.Subscript` under a `Store` — and name `obj.at_put(key, value)` there,
keeping `obj.at(key)` for a `Load`. The slice branch needs the same split or an
honest refusal: `xs[1:3] = ys` has no substitute either, and today it is
answered by the message about `obj.slice(...)`, which reads. `INFECTIONS.md`'s
`no_subscript` table grows the second row.

---

### 19. `Dict.do` disagrees with every other way of iterating a `Dict`

`Dict.do` overrides the mixin's to yield `(key, value)` pairs. Nothing else on
the same receiver agrees with it:

```
d = {"a": 1}
d.do(lambda x: x.print())            # a 1        — a pair
list(d.map(lambda x: x)).print()     # a          — a key
list(d.filter(lambda x: True)).print()  # a       — a key
d.sorted().print()                   # a          — a key
d.min().print()                      # a          — a key
d.iter().next().print()              # a          — a key
```

So `d.do(lambda k: k.upper())` — the shape every `List` example in `examples/`
teaches — answers `tuple does not understand #upper`, while `d.map(lambda k:
k.upper())` works. One receiver, two answers to "what is an element of a
`dict`", and the one that differs is the message `no_loops` names as the
substitute for `for k in d`, which in Python walks the keys.

**Fix.** Make `do` yield keys like its five siblings and like Python's `for`,
leaving `d.items().do(...)` as the pair spelling that already exists (and
already answers `Tuple`s). The mutation guard `Dict.do` carries stays — it is
about iterating the dict, not about what it yields. This is a breaking change
for any program written against the pair form, so it wants a sweep of
`examples/` and the docstring in `INFECTIONS.md` in the same commit; the
alternative — pairs everywhere — contradicts `iter()`, `reversed()` and Python,
and would need six methods changed instead of one.

---

### 20. `With` hands `__exit__` three raw Python values

`Try` wraps what it catches: a handler receives an `Error`, which answers
`message()`, `kind()` and `class_name()`, and `poop/types/error.py` spends four
docstrings on not leaking the wrapper. `With` hands the other half of the same
job straight to CPython — `exit_(cm, type(e), e, e.__traceback__)` — so a
user's `__exit__` receives values no POOP message works on:

```
class R(Object):
    def __enter__(self):
        return 1
    def __exit__(self, kind, err, tb):
        kind.is_none().print()   # 'NoneType' object has no attribute 'is_none'
        err.message().print()    # 'ZeroDivisionError' object has no attribute
        return False             #  'message'

With(lambda: R()).do(lambda x: (1 / 0))
```

Three separate leaks in one call. `kind` is the *native* class, not the mirror,
so it is not even the object `Try(…).except_(ZeroDivisionError, …)` matches
against and no program can name it. `err` is the bare exception rather than an
`Error`. `tb` is a traceback object — a whole introspection surface, reached
through `__traceback__`, the dunder spelling `no_dunder_attribute` refuses. And
on the success path all three are Python's `None`, not POOP's `none`, so the
first thing an `__exit__` would ask (`kind.is_none()`) fails there too.

The class docstring's "deliberate primitive leak" covers the *protocol* — that
a manager must define `__enter__`/`__exit__` — not the values passed through
it; `_protocol` already goes out of its way to keep `__exit__` out of the
refusal it composes one method above.

**Fix.** Pass what `Try` passes: `poop_class_of(e)` for the kind, `Error(e)` for
the exception, and `none` for the traceback — POOP has no traceback object and
inventing one would hand back the introspection surface. On the success path
send `none` three times. The signature stays three arguments, so a manager
written for Python's shape still binds, and the `With` receiver test in
`tests/test_types/test_with_.py` grows a case that *reads* each argument rather
than only counting them. `examples/` has no `With` program at all today — one
belongs in the same commit, since this protocol is now the only place a POOP
program meets a dunder it must implement itself.

---

### 21. A user class cannot satisfy the protocol slots it is allowed to define

`class P(Object)` may define dunders — `__init__`, `__eq__`, `__lt__`,
`__enter__` and `__add__` all work, and `CONTRIBUTING.md` tells a contributor to
"wire dunders to public Python-named methods". But a POOP program can only
produce POOP values, and four of those slots are read by CPython, which demands
a native one:

```
class P(Object):
    def __str__(self):
        return "P!"
P().print()      # TypeError: __str__ returned non-string (type str)

    def __repr__(self):   # TypeError: __repr__ returned non-string (type str)
    def __bool__(self):   # TypeError: __bool__ should return bool, returned bool
    def __hash__(self):   # TypeError: cannot use '__poop__.P' as a set element
                          #            (__hash__ method should return an integer)
```

Each sentence is self-contradicting, because `_cloak` renamed the wrapper to the
builtin it stands for: `__str__ returned non-string (type str)` names `str` as
the thing that is not a `str`, and `__bool__ should return bool, returned bool`
is a sentence with no information in it at all. All four name a dunder, which is
the leak items 3, 5 and 10 exist to close, and the `__hash__` one additionally
prints `__poop__.P` — the internal module marker `poop/types/meta.py` uses to
tell a user's class from a builtin, which no program should ever see.

There is no workaround: the value a POOP method can return is exactly the wrong
kind. `__len__` is the quiet member of the family — defining it raises nothing
and does nothing, since `len` is a message and `P` does not understand it.

**Fix.** Adapt the four slots where the class is built. `PoopMeta` is on every
POOP class already (`ClassTransformer` routes every user class through
`Object`) and a `__new__` there sees the namespace before the class exists:
wrap a user-defined `__str__` / `__repr__` /
`__bool__` / `__hash__` so the POOP value it answers is unwrapped through
`_bridge.to_python` on the way out, and refuse — in POOP's words, naming the
message rather than the slot — anything that is not a `Str` / `Boolean` / `Int`.
The wrapper classes are unaffected: they define these slots in
`poop/types/`, in Python, and already return natives. `__len__` is the separate
half: either wire `Object.len` to a user `__len__` or leave it out of the
allowance, but it should not be a slot that silently does nothing.

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
