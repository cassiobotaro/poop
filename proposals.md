# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Every claim below was verified by running the interpreter; the quoted output is real.

---

## Doctrine holes

Constructs that survive today but that POOP's own stated rules reject. Each has
a substitute that already exists, so each is a validator away from closed.

### ~~1. Chained comparison smuggles the lazy `and` that `no_and_or` forbids~~ — DONE

**Decision: allow.** `a < b < c` stays legal; no validator is added. Recorded in
`INFECTIONS.md` under *Explicitly allowed* → *Binary infix operators*, whose
entry already named `ast.Compare` without qualifying the single-`op` case.

The case for banning was real, and is kept here so it is not re-derived from
scratch. The construct delivers `no_and_or`'s short-circuit semantics with no
`and` token — verified: `(1 < x) and (x < 10)` is rejected while `1 < x < 10`
answers `True`, and a `Probe` evaluated as `p < p < p` printed once, confirming
CPython short-circuits the chain. `no_and_or` never sees it because it visits
`ast.BoolOp` only. Smalltalk cannot express the form at all: `1 < x < 10` parses
as `(1 < x) < 10`, sending `#<` to a Boolean, which answers `doesNotUnderstand:`.

It loses on blast radius. `a < b < c` expands to `(a < b) and (b < c)`, whose two
conjuncts are forced to share the middle operand — no arbitrary `P and Q` is
reachable through a chain. The construct is a range check, not a general `and`
escape hatch, and banning it would cost every range check in the language its
Python-obvious spelling to close a gap that admits only range checks.

Note what this allowance rests on: **Python ergonomics, not the absence of a
substitute**. `(1 < x).and_(lambda: x < 10)` exists and works. Every other entry
in *Explicitly allowed* turns on "no principled substitute exists"; this is the
first that does not, and that is deliberate. Item 2 has since faced the same
trade-off over raw dunder calls and settled it the other way: unlike a chain,
`xs.__len__()` both leaks a raw primitive and has a substitute, so ergonomics
had nothing to weigh against.

### ~~2. Dunder attribute access reproduces banned builtins verbatim~~ — DONE

`no_introspection` bans `vars(obj)` because it "exposes raw Python-native slot
values… breaks encapsulation and the 'all methods return POOP types' rule". But
`vars(obj)` *is* `obj.__dict__`, and the attribute spelling passes:

```
A().leak().print()   →  poop: 'dict' object has no attribute 'print'
```

A raw CPython `dict` reached runtime, against the principle that "no naked
Python primitive ever reaches runtime". The same applies to `x.__class__`,
`A.__mro__` and `A.__bases__`, which reconstruct the `type(x)` that `no_type`
bans for "returning a raw class object that is not a POOP value".

Root cause: `_call_name.py` visits `ast.Name`, never `ast.Attribute`.

**Decision: closed by rule, with a runtime guard.** `no_dunder_attribute`
rejects any `__dunder__` in `ast.Attribute` position, `__init__` excepted, and
`Object._reject_dunder` closes the spelling no validator can see. Both halves
read one `dunder_message`, so the ban says one thing.

Everything this item argued held on implementation, and each ground is recorded
in `INFECTIONS.md` rather than here: the rule beats the list (the four obvious
names had already missed `__name__`); the runtime guard is mandatory because
`get_attr("__dict" + "__")` is invisible statically; `__init__` must be carved
out or `super().__init__()` breaks a standing allowance; and raw dunder calls
are in, because CPython forces `__len__` and `__contains__` to answer raw
primitives while `__abs__` costs nothing to lose.

The messages name their substitute — `.__len__ is forbidden — use obj.len()
instead` — rather than refusing generically. The rule still governs: an unnamed
dunder answers "dunders are Python's protocol, not POOP's message surface".

**Item 4 came true, exactly as predicted here.** `(5).__class__.print()` now
answers `int` — `PoopMeta` made it a real POOP class, so it is no longer a
doctrine hole. It stays banned on this item's second ground: a non-Smalltalk
spelling of `x.class_()`.

**Item 9's guard test caught the omission.** Adding the validator failed
`test_every_validator_is_reachable_from_explain` — the new ban had no
`:explain` topic. That test exists because five constructs went missing exactly
this way.

### ~~3. `...` is the only untransformed literal~~ — DONE

**Decision: transform, do not ban.** `...` now answers `EllipsisClass`'s
`ellipsis` singleton. Implemented in `poop/types/ellipsis.py` +
`poop/transformers/ellipsis.py`; catalogued in `INFECTIONS.md`.

The hole was real — `x = ...; x.class_name()` used to answer `poop: 'ellipsis'
object has no attribute 'class_name'`, making "**Every literal is transformed** …
no naked Python primitive ever reaches runtime" false as written.

A ban was considered and rejected. It would have taught nothing about message
passing — `...` is not procedural, so rejecting it is hygiene, not doctrine —
and it would have left the invariant closed by exception rather than by rule.
Transforming keeps the invariant literally true, and `NoneClass` is the exact
precedent: a singleton wrapping a placeholder, with no behaviour of its own
beyond the `Object` protocol. The surface criterion ("a message earns its place
only when it substitutes a forbidden construct") does not bar this: it governs
*messages* and stdlib parity, whereas `...` is a **literal**, and the doctrine
already commits to transforming every literal and giving every basic type a POOP
equivalent. `EllipsisClass` adds no messages at all.

Implementation note worth keeping: the transformer rewrites **both** spellings —
`ast.Constant(value=Ellipsis)` and `ast.Name(id="Ellipsis")`. Verified that
`x = Ellipsis` reached runtime as the raw primitive too, so rewriting only the
literal would have moved the hole rather than closed it. Same shape as item 2's
`vars()` / `obj.__dict__` asymmetry.

Also verified, and recorded in `INFECTIONS.md`: POOP's examples declare no
abstract methods at all — the base class omits the message and lets polymorphism
supply it — so `...` has no idiomatic role in POOP. All 8 occurrences of `...` in
`examples/` sit inside docstrings, quoting the Python that POOP forbids.

---

## Language features

### ~~4. Classes are not objects~~ — DONE

The deepest remaining gap, and the one most central to Smalltalk. Classes do not
answer messages:

```
Foo.print()   →  poop: Object.print() missing 1 required positional argument: 'self'
```

The project already works around this in three places, each documenting the same
missing piece:

- `no_type` bans `type(x)` for "returning a raw class object that is not a POOP
  value" and settles for `class_name()` — a `Str`, i.e. a class's *name* standing
  in for the class.
- `is_instance(T)` is documented as a "deliberate primitive leak: POOP has no
  first-class metaclass or class-object type, so there is nothing more idiomatic
  to pass".
- `Try.except_(ValueError, …)` leaks the same way.

A metaclass closes all three at once. `ClassTransformer` already reroutes every
user class through `Object`, so the metaclass propagates for free.

**Decision: `PoopMeta`, with the protocol the surface criterion admits.**
`Foo.print()` answers `Foo`. The class side is `name()`, `superclass()`,
`has_attr()`, `print()` and `does_not_understand()`; `x.class_()` answers the
class object, and `class_name()` is now `x.class_().name()`.

**Two of the five proposed messages did not survive the criterion.** `new(...)`
is out: `Foo()` already builds an instance and is not forbidden, so `Foo new`
would be parity, not substitution — the bar *Considered and rejected* set for
cascades and `yourself`. And `responds_to` is spelled `has_attr`, per
`CONTRIBUTING`'s naming rule ("`filter`, not `select`") and the instance side.
The three that stay each substitute a ban: `name()` for `type()`, `print()` for
`print`, `superclass()` for the `__bases__`/`__mro__` that item 2 will ban — and
it has to exist first, by "activate a validator only when the substitute exists".

**The prototype in this item tested only `name()`, and that hid the real
problem.** Attribute lookup on a class searches the class's own MRO *before* the
metaclass, so a plain `PoopMeta.print` is never reached: `Object.print` wins and
answers `Object.print() missing 1 required positional argument: 'self'` — the
exact symptom this item exists to remove. `name()` worked only because `Object`
happens not to define it. Every class-side message is therefore a **data
descriptor** (`class_side`), which lookup does consult first. Instances are
untouched: instance lookup never consults the metaclass, so `Foo().print()`
still finds `Object.print`. Verified both ways, including a user class declaring
its own `name` method — the class side still answers.

The `ABCMeta` constraint held exactly as recorded, and the metaclass propagates
with nothing declaring it.

**`Object superclass` answers `none`**, mirroring Smalltalk's `nil`. That is also
what keeps the raw Python `object` at the root out of reach.

**Classes now answer `doesNotUnderstand:` too.** Item 6 gave the hook to
instances only, since `Object.__getattr__` is instance-level — leaving
`(5).frobnicate()` answering "int does not understand #frobnicate" while
`Foo.frobnicate()` still answered "type object 'Foo' has no attribute". The
metaclass is where that hook was missing.

**Found while implementing, and still open**: a bare `object` in POOP source is
never rewritten and reaches runtime as the raw CPython class —
`object.class_name()` answers `type object 'object' has no attribute
'class_name'`. Every other lowercase builtin gets a `Name`-position rewrite
(`int.name()` answers `int`); `object` is rewritten only in class-base position,
by `ClassTransformer`. `CLAUDE.md`'s "lowercase Python builtins (`int`, `list`,
`object`, …) get rewritten" is inaccurate for exactly one name. Pre-existing, and
its own item.

Scope note, now settled: `no_type`'s substitute column and `is_instance` are
closed by this. `Try.except_` is **not** — `ValueError` is a raw CPython class
that never passes through `Object`, so `PoopMeta` cannot reach it. That third
leak needs item 12.

### ~~5. `Try` and `With` are the only blocks that swallow their value~~ — DONE

Verified — this prints `Try`, not `42`:

```python
result = Try(lambda: int(text)).except_(ValueError, lambda e: -1).run()
result.print()
```

`Try._execute()` and `With.do()` both discard the block's result and return
`self`.

This is an internal inconsistency rather than a design stance: POOP's other
blocks already answer values, Smalltalk-correctly — `if_true_if_false`,
`if_none` and `if_not_none` all verified returning the block's value. The
Smalltalk twin in `examples/idiomatic/safe_config.py` assigns straight from
`ifNotNil:ifNil:`, and `on:do:` / `ensure:` answer values the same way.

The consequence is that `try: return f() except: return default` has **no**
substitute. The only way to get a value out of a `Try` today is to mutate a
closure-captured collection:

```python
box = []
Try(lambda: box.append(int(text))).except_(ValueError, lambda e: box.append(-1)).run()
return box.at(0)
```

That is the imperative, side-effecting style POOP exists to eliminate — and it
puts `no_try` in violation of "**Activate validator only when the substitute
exists**".

**Decision: answer the value.** `.run()` / `.finally_()` answer the protected
block's value, or the matching handler's when one fires; `With.do()` answers the
body's. `no_try` now has the substitute it always advertised:

```python
return Try(lambda: int(text)).except_(ValueError, lambda e: -1).run()
```

**The breaking change cost one line of production code and five tests.** Nothing
in `examples/` chains off `.run()` / `.do()` / `.finally_()`, and no test asserts
the returned value for its own sake — the five that broke all used
`t = Try(...).run()` merely to get the `Try` back and probe the single-use
invariant. Binding the `Try` first tests the same thing and depends on nothing.
`feat!` still stands for anyone outside this repo.

The one test that did lock the old contract was `test_with_returns_self_for_chaining`
— and `With`'s entire public API is `__init__` and `do()`. There was never
anything to chain onto; the test enshrined a rationale that never existed.

**Found while implementing: `With.do()` has a path with no body value.** When the
body raises and `__exit__` suppresses it, the body never produced anything to
answer — this proposal said "answers the body's value" and did not define the
case. It answers `none`, mirroring Python, where a suppressed exception simply
carries on past the block.

### ~~6. No `doesNotUnderstand:`~~ — DONE

An unknown message is phrased in Python's vocabulary, for a language whose thesis
is that everything is a message:

```
x.frobnicate()   →  poop: 'int' object has no attribute 'frobnicate'
```

It says *attribute*, not *message*, suggests nothing, and does not point at
`:methods`. `AttributeError` carries `.name` and `.obj`, which the error path
discards. `difflib.get_close_matches` against `dir(obj)` performs well on the
real types — `uppercase → ['upper', 'isupper']`, `lenght → ['len']`, and notably
`ifTrue → ['if_true']`, so a Smalltalker typing Smalltalk's actual selector
currently hits a dead end.

Beyond the message, the hook is the metaobject-protocol feature that makes real
proxies possible (cf. `examples/patterns/proxy.py`).

**Decision: the hook, plus a written-down selector table.** `Object.__getattr__`
routes unknown messages to `does_not_understand(name)`, which answers
`MessageNotUnderstood: int does not understand #frobnicate — try :methods to
list its messages`. Overriding it is the metaobject hook proxies need.

**The Smalltalker argument in this item was luck, not evidence.** It cited
`ifTrue → ['if_true']` as proof `difflib` performs well. Measured against ten
real selectors it scores **3/10** — `printNl`, `do:`, `ifTrue:`, exactly the
three where both languages chose the same word — and answers confidently wrong
on the rest: `size` → `slice`, `inject:into:` → `insert`, `notNil` → `not_`.
`difflib` measures *string* similarity; Smalltalk → POOP is a *vocabulary*
mapping, and no cutoff bridges `size` to `len`, which share no letters. Hence
`poop/types/_selectors.py`, a table of the selectors POOP spells differently. A
test asserts every entry maps to a message some POOP type actually answers — a
table teaching a name that fails on the next line would be worse than none.

**The cutoff is 0.7, not difflib's 0.6.** With the table carrying the
vocabulary, `difflib`'s only remaining job is typos. Measured over six real
typos and four nonsense names: 0.6 caught 6/6 but invented `frobnicate` →
`from_bytes` and `blerg` → `clear`; 0.7 caught 5/6 and invented nothing. Losing
`lenght` → `len` costs less than confidently naming a message nobody meant.

**Three implementation constraints this item did not raise**, each verified:

- *`MessageNotUnderstood` must inherit `AttributeError`* — ironic for the error
  that exists to stop speaking Python, but `hasattr` and three-argument
  `getattr` swallow that and nothing else. A plainer base breaks
  `Object.has_attr` and `get_attr(name, default)`, POOP's own substitute for the
  banned `getattr`. Verified: all three crash without it.
- *Dunders must never reach the hook* — Python probes every object for
  `__copy__` / `__getstate__`, and a proxy would answer those probes as if a
  user had sent them.
- *`__getattr__` must be hidden behind `if not TYPE_CHECKING`* — a visible one
  answers `Any` for every name, so `xs.frobnicate()` would type-check on every
  POOP object and `ty` would stop catching typos codebase-wide. The two
  `ty: ignore[unresolved-attribute]` comments in `test_list.py` going *unused*
  is what surfaced it. Statically an unknown message is still an error; the hook
  changes what happens when one is sent, not what is knowable before.

The signature is `does_not_understand(name)`, not `(name, args)` as proposed:
attribute lookup runs before the call, so nothing there has seen the arguments.
An override reaches them by answering a callable, which is what a proxy does
anyway.

Worth recording: item 7 made this item *sharper*. Adding the exception class
name means the message now reads `poop: AttributeError: 'int' object has no
attribute 'frobnicate'` — literally naming a Python class in a language whose
thesis is that everything is a message.

### ~~12. Exception types are the last raw primitive in the `Try` surface~~ — DONE

Numbered out of document order deliberately: items are stable identifiers —
`CONTRIBUTING.md` closes them as `docs: close proposal N` — so 7–11 were not
renumbered to make room.

`Try.except_(ValueError, handler)` and `ValueError.raise_("msg")` both take a
native CPython class. `INFECTIONS.md` calls it "the only deliberate primitive
leak" and justifies keeping it: "Mirroring Python's full hierarchy (~100+
classes) into POOP types is impractical." That justification does not survive
measurement, on two counts.

**The number is wrong.** Python 3.14 has **71** builtin exceptions, not 100+.
Eighteen are the `OSError` subtree and five are `Unicode*` — unreachable in a
language with no I/O and no codecs. Probing real failures through the
interpreter reaches eight (`IndexError`, `KeyError`, `ValueError`,
`ZeroDivisionError`, `AttributeError`, `TypeError`, `NameError`,
`StopIteration`); `poop/types/` raises three more (`RuntimeError`,
`AssertionError`, `NotImplementedError`). Call it ~11, plus the abstract
groupers worth naming (`Exception`, `LookupError`, `ArithmeticError`).

**And mirroring needs no translation layer at all** — the load-bearing find.
`Try._execute()` catches `except BaseException` and then matches with
`isinstance(e, exc_type)`: **POOP's own code, not Python's `except` clause**. So
POOP decides what each class matches, via `__instancecheck__`. The obvious
objection — "a POOP `ValueError` subclassing CPython's would not catch the
parent, since `except Subclass` does not catch a superclass" — never applies,
because no Python `except` clause ever sees a user-supplied type.

**Proposal**: mirror the reachable exceptions as POOP classes subclassing their
native twin — staying raisable, which is what `raise_` depends on — with the
metaclass deciding the match:

```python
class PoopExcMeta(PoopMeta):        # item 4's metaclass, already ABCMeta-derived
    def __instancecheck__(cls, obj):
        native = cls.__dict__.get("_native")   # not inherited — see the trap
        if native is None:
            return super().__instancecheck__(obj)
        return isinstance(obj, native)
```

**Verified end-to-end** in the interpreter, mirrors injected into the namespace,
catching raw CPython exceptions raised from inside POOP's own wrappers:

| program | result |
|---|---|
| `Try(lambda: int("abc")).except_(ValueError, …)` | caught the raw `ValueError` |
| `Try(lambda: {"a": 1}.at("zzz")).except_(LookupError, …)` | caught the raw `KeyError` |
| `Try(lambda: [1, 2].at(99)).except_(LookupError, …)` | caught the raw `IndexError` |
| `Try(lambda: {"a": 1}.at("zzz")).except_(ValueError, …)` | no match, re-raised |
| `Try(lambda: ValueError.raise_("boom")).except_(ValueError, …)` | `boom` |

**Verified trap: `_native` must not be inherited.** A user's
`class MyError(Error)` inheriting `_native = Exception` makes
`except_(MyError, …)` catch *every* exception in the program — silent and total.
Reading `_native` from `cls.__dict__` only, and falling back to normal
behaviour, fixes it: mirrors match their native twin, user subclasses match
themselves. The obvious alternative — `__init_subclass__` setting
`_native = cls` — recurses infinitely, since `__instancecheck__` then calls
itself. Twelve cases verified, including a user class inheriting from a mirror.

**Depends on item 4**, and strengthens it. The metaclass derives from `PoopMeta`,
so exception classes become POOP class objects for free, answering `name()`. And
`ValueError.raise_("boom")` stops being AST theatre: the `raise_` transformer
today rewrites it to `_poop_raise(ValueError, "msg")`, matching any uppercase
`Name` followed by `.raise_(...)`, precisely *because* classes cannot receive
messages. That is a fourth workaround for item 4 beyond the three it lists; the
fifth is `Error.kind()` answering a `Str` of the type's name — the same
substitution `class_name()` makes, a name standing in for the class.

**Not a stdlib mirror.** The *Considered and rejected* entry bars mirroring
*modules*. Builtin exceptions are builtins, like `int` and `list`, which POOP
already wraps. And both substitutes POOP mandates for forbidden constructs —
`Try.except_(T, …)` for `try`, `T.raise_(…)` for `raise` — take an exception
class as an argument, so these classes are load-bearing surface, not parity.

**Closed as proposed, with the three open questions settled and one addition.**
Sixteen mirrors; `Try.except_(ValueError, h)` catches the raw `ValueError` that
`int("abc")` raises from inside the `Int` wrapper, and `Error.kind()` answers the
POOP class.

- *Names reach user code by transformer*, as suggested — `DEFAULT_NAMESPACE`
  stays exactly `Try` and `With`. **It must run after `RaiseTransformer`**: that
  one matches an uppercase `ast.Name` followed by `.raise_(...)`, and
  `_poop_ValueError` is not uppercase, so the wrong order silently stops
  `raise_` from being recognised at all.
- *`Error.kind()` answers the POOP class.* It was the same substitution
  `class_name()` made — a name standing in for a class — and survived only
  because POOP had no class objects to answer with. Item 4 fixed that.
- *The root does inherit `Object`* — verified, no layout conflict. A user's
  `class MyError(Exception)` now lands inside the Object tree and answers
  `class_name()`, closing a hole this item only noted in passing.

**`RecursionError` was missing from the measured set**, and it is the most
reachable of all: recursion is POOP's substitute for every loop. Verified —
`(n > 0).if_true_if_false(lambda: self.down(n - 1), ...)` at depth 100000
answers `poop: RecursionError: maximum recursion depth exceeded`.

**The breaking change bit an example.** `bank_account.py` wrote
`"Error [" + e.kind() + "]"`, which a class cannot be concatenated into; it is
now `e.kind().name()`. Nothing else in the repo depended on `kind()` answering a
`Str`.

**Depends on item 4, as recorded** — `PoopExcMeta` derives from `PoopMeta`, so
the mirrors answer `name()`, `print()` and `superclass()` for free:
`KeyError.superclass().name()` answers `LookupError`. And item 4's third leak,
which `PoopMeta` alone could not close, is closed here.

---

## Error reporting and the REPL

The error machinery is sound and should be credited: `__module__`/`__name__`
masking plus `_user_lineno`'s frame-walk mean no `_poop_*` name, transformer
frame, or Python traceback ever reaches the user, and the reported line is the
deepest *user* frame. The gaps are in what is thrown away on the way out.

### ~~7. `ExecutionError` destroys the exception class name~~ — DONE

**Decision: prefix the class name.** `_describe()` in `poop/executor.py` answers
`f"{type(exc).__name__}: {exc}"`, so a missing key reads
`poop: KeyError: 'zzz' (line 1)` where it used to read a bare `poop: 'zzz'` —
a quoted string with nothing to say a lookup had failed.

The proposal's safety argument needed correcting, though its conclusion held. It
claimed "type names are already masked to builtins, so this leaks no internals".
The masking is real (`Int.__name__ = "int"`) but sits on POOP's *value* wrappers
and never applies here: exceptions are never wrapped, so `type(exc).__name__` is
CPython's own name, or a user's. Nothing on this path is a `_poop_*` name to
begin with — that, not the masking, is why it is safe.

Found while implementing: the formula mishandles an empty message.
`ValueError.raise_()` reaches the executor with `str(exc) == ""` and rendered
`poop:  (line 1)` — worse than this item described — and
`f"{type(exc).__name__}: {exc}"` would answer `poop: ValueError:  (line 1)`,
colon dangling. `_describe()` degrades to the bare name instead.

The `SyntaxError` branch above it is deliberately untouched: it already converts
Python's message into a POOP-level one, and prefixing `SyntaxError:` would
restore the vocabulary that branch exists to hide.

### ~~8. The REPL renders errors worse than the file runner~~ — DONE

**Decision: hoist into `poop/errors.py`, and state the position once.**
`format_error()` is shared by `cli.py` and `repl.py`, so one program reports the
same way on both surfaces. The REPL now draws the gutter and caret it always had
the source for:

```
poop: print is forbidden — use obj.print() instead
  1 | print(x)
    | ^
```

It went to `errors.py` rather than a new module: `PoopError` lives there and both
surfaces already imported from it, so the hoist added no module and no import.

**Narrower than "use it in both" suggests.** Of the REPL's three error sites only
one is a `PoopError` holding the source — the other two are a `:methods`
evaluation failure and a `codeop` `SyntaxError`, neither carrying a POOP
position. The REPL also colours errors red where the CLI does not, so the
formatter answers plain text and the REPL wraps it.

**On dropping `(line 1, col 0)`:** this item asked for it on single-line REPL
input, but that is a special case of a general rule. Where the source line is in
view the gutter states the line and the caret the column, so the suffix merely
repeats them. It is now dropped whenever the gutter is drawn — on both surfaces,
which is a change to the file runner this item did not ask for — and kept
whenever it is not: no source, or a line number out of range, where it is the
only clue left. `TransformError`'s `(transformer X)` is not a position and
survives untouched.

### ~~9. `:explain` denies the project's central doctrine~~ — DONE

**Decision: derive what can be derived, assert the rest.** `:explain import` now
answers "POOP is the language, not the library". `_EXPLAIN_CALLS` is computed
from `DEFAULT_VALIDATORS`, the five missing syntax snippets are added, the
fallback no longer guesses, and a test fails when a validator has no topic.

**The gap was seven, not five.** This item read only the syntax side. Comparing
the 51 names declared by the call-name validators against the 49 hand-written in
`_EXPLAIN_CALLS` also caught `delattr` and `__import__` — both banned, both
answered with "it may simply be allowed".

**"Derive from `DEFAULT_VALIDATORS`" splits, and only half is reachable.** The
call half is real: `make_call_name_validator` closes over its `forbidden` set,
now exposed as a class attribute, so `_EXPLAIN_CALLS` is derived and that class
of drift is gone for good. The syntax half is not: `make_node_validator` knows
AST node *types*, and there is no mechanical path from `ast.If` to
`"if x:\n    pass"` — synthesising nodes for `ast.unparse` means inventing
operands (`ast.Compare` + `ast.In`), which is more fragile than the dict it would
replace. That half is guarded by a test instead: every validator must be tripped
by some topic. Where derivation is impossible, assert.

Three validators are exempt, deliberately. `NoPoopPrefix`, `NoNamespaceShadow`
and `NoBuiltinShadow` answer name *choices* rather than constructs — there is no
word a learner could type at `:explain` to reach them.

Worth keeping, because this item undersold it: `:explain` stores no explanations.
It stores a snippet per topic, runs it through `validate_all()`, and prints the
validator's own message. Only the topic list could ever drift — never the
wording.

Found while implementing: `test_meta_explain_every_known_construct_produces_output`
asserted `"forbidden" in out` as a proxy for "a validator spoke", and held only
by luck of wording — `no_unary_minus` answers "allowed only on numeric literals"
and broke it. It now asserts the two non-explanation branches directly.

### ~~10. One error per validator, in registration order~~ — DONE

**Decision: collect, then sort.** `collect()` is now the validator primitive and
`validate()` is derived — "raise the first error `collect` found" — so
`--validators-only` reports every occurrence in source order while running a
program still fails fast. Three `if`s answer three errors; errors on lines 3, 4,
5, 6 came back as 5, 6, 4, 3 and now come back in order.

Collecting had to be the primitive rather than the derived one: a raise has
already thrown away the rest of the walk, so all-errors cannot be rebuilt from
first-error. Keeping `validate()` in the protocol carried its weight — 409 tests
call it, and its contract is unchanged.

Eight visitors needed the change, not the three factories alone:
`no_free_functions`, `no_subscript`, `no_poop_prefix` and the visitor shared by
`no_namespace_shadow` / `no_builtin_shadow` are hand-written.

**Two traversal decisions this item did not raise:**

- *Descend into a rejected node.* `make_node_validator` stopped at the first
  banned node and never recursed. An `if` nested in an `if` is two rewrites, and
  reporting only the outer one restores the fix-one/rerun loop this item exists
  to end — so the walk now continues into it.
- *One error per `Compare`, not per banned op.* `a in b in c` is one node and one
  rewrite. `_op.py` already promised "rejects the first banned op"; a `break`
  keeps that true now that the loop no longer exits by raising.

Still true, and out of scope: running a program reports the first *validator*
that fires, not the earliest error in the file — `poop f.py` cites line 5 where
`--validators-only` starts at line 3. This item scoped itself to
`--validators-only`. Closing that one means running all 66 validators before
reporting, which is cheap on an error path but is its own decision.

---

## Documentation

### ~~11. `INFECTIONS.md` contradicts itself on `help`~~ — DONE

**Decision: the ban is real; the allowance was stale.** The *Explicitly allowed*
entry for `help` is removed; the *Active infections* entry stands unchanged.

`help` was listed under **Active infections** ("No `help`") *and* under
**Explicitly allowed** ("Allowed."). Reality settled it: `NoHelpValidator` is in
`DEFAULT_VALIDATORS`, and `help(5)` answers `poop: help() is forbidden — no POOP
equivalent`.

The two entries disagreed on more than status, which is why the stale one went
rather than the ban. *Explicitly allowed* argued `help()` "carries no program
logic and has no message-passing equivalent that would be more expressive" —
harmless dev tool, allow. *Active infections* argues it is an "interactive escape
hatch (opens the Python pager) exposing wrapper internals". The second is the
better reading and matches the code: the pager renders raw `_poop_*` internals,
which is the same leak `no_introspection` and item 2 exist to close.

Verified alongside: `dir`, the sibling case, appears only under *Active
infections* — no twin entry. `help` was the lone leftover, not a pattern.

---

## Considered and rejected

- **stdlib mirrors of any kind** — settled: POOP is the language, not the
  library.
- **Cascades (`;`) and `yourself`** — Smalltalk-shaped, but they substitute no
  forbidden construct, which is the bar a new message has to clear.
- **`%` / `.format()`** — already the sanctioned surface replacing f-strings.
- **`@property` / `super()` / `+=` / binary operators** — explicitly allowed by
  design, with stated rationale.
