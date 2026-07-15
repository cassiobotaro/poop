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

### 2. Dunder attribute access reproduces banned builtins verbatim

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

**Proposal**: a `no_dunder_attribute` validator rejecting **any** `__dunder__`
in `ast.Attribute` position, with `__init__` carved out, plus a runtime guard on
`Object.get_attr` / `has_attr` / `set_attr` / `del_attr`. Close by rule, not by
list. Not yet implemented; the four grounds below are each verified.

**Why a rule, not the four obvious names.** The list `__dict__`, `__class__`,
`__mro__`, `__bases__` is already incomplete: `x.__class__.__name__` answers a
raw `str`. Enumeration invites the next omission, and item 3 settled this same
argument — an invariant closed by exception is not closed.

**Why a runtime guard too.** `no_getattr` bans `getattr` and offers
`obj.get_attr(name)` as the substitute — and `A().get_attr("__dict__")` reopens
the exact hole the validator would close. Worse, `name = "__dict" + "__"` then
`A().get_attr(name)` leaks the same `dict`, so **no static validator can see this
spelling**; the guard has to live in `Object`. Same shape as the
`vars()`/`obj.__dict__` asymmetry that opens this item, and as item 3's
`...`/`Ellipsis` double spelling.

**Verified constraint: `__init__` must be carved out.** `super().__init__(name)`
is an `ast.Attribute` with a dunder attr, and it runs today. `INFECTIONS.md`
allows `super` explicitly — "without it, subclasses cannot extend parent
behaviour — inheritance breaks entirely. There is no message-passing substitute."
A blanket rule would contradict a standing allowance.

**Raw dunder calls: in, and not on taste.** `x.__len__()`, `(5).__abs__()` and
`col.__contains__(x)` are not one case. CPython *forces* `__len__` to answer a
real `int` and coerces `__contains__` to a real `bool`; the signatures record the
surrender — `def __len__(self) -> int` and `def __contains__(...) -> bool`,
against `def __abs__(self) -> Int`. Verified: `(5).__abs__().class_name()`
answers `int`, while `xs.__len__().class_name()` fails on a raw `int`. So
`__len__`/`__contains__` are structurally incapable of honouring the doctrine,
while `__abs__` already honours it. The rule bans both regardless: losing
`(5).__abs__()` costs nothing — `.abs()` exists and nobody writes the dunder —
and sparing it would restore the exception list the rule exists to avoid.

**Substitutes**: all present, so "activate a validator only when the substitute
exists" is satisfied — `.len()`, `.includes()`, `.abs()`, `.hash()`, and
`x.class_name()` or polymorphism. For `__dict__`, none: the ban is the decision,
exactly as `no_introspection` already argues for `vars`.

**Interaction with item 4**: `x.__class__` leaks a class object, not a raw
primitive. If `PoopMeta` lands it answers a real POOP class and stops being a
doctrine hole, becoming merely a non-Smalltalk spelling of `x.class_()`. The ban
stands either way, on that second ground.

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

### 4. Classes are not objects

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

**Proposal**: `PoopMeta` providing the class-side protocol — `name()`,
`superclass()`, `new(...)`, `responds_to(...)`, `print()` — and `x.class_()` on
`Object` answering the class object itself (Smalltalk's `x class`), with
`class_name()` becoming `x.class_().name()`.

**Verified constraint**: `PoopMeta` **must** derive from `ABCMeta`, not `type`.
`Boolean(Object, ABC)` otherwise fails with `metaclass conflict: the metaclass of
a derived class must be a (non-strict) subclass of the metaclasses of all its
bases`. With `ABCMeta` as the base, a prototype worked and subclasses inherited
the metaclass automatically.

Scope note: this touches `no_type`'s substitute column, `is_instance`, `Try`, and
`INFECTIONS.md`'s primitive-leak tradeoffs. Worth agreeing on the class-side
protocol before any code.

### 5. `Try` and `With` are the only blocks that swallow their value

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

**Proposal**: `.run()` / `.finally_()` answer the protected block's value, or the
matching handler's value when one fires; `With.do()` answers the body's value.
Builder chaining is unaffected — both are terminal. `finally_`'s cleanup value is
discarded, mirroring Smalltalk's `ensure:`.

**Breaking**: `feat!`. Code relying on the returned `Try`/`With` changes meaning.

### 6. No `doesNotUnderstand:`

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

**Proposal**: `Object.__getattr__` routing unknown messages to a
`does_not_understand(name, args)` hook, default raising
`poop: Int does not understand #frobnicate` plus `did you mean:` and a
`try :methods x` pointer. Verified compatible with `__slots__`; normal message
lookup is untouched (`__getattr__` fires only on miss).

### 12. Exception types are the last raw primitive in the `Try` surface

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

**Open questions**:

- How the names reach user code. `CLAUDE.md` states `DEFAULT_NAMESPACE` is
  "exactly two names — `Try` and `With`". A transformer rewriting
  `ast.Name(id="ValueError")` → `_poop_ValueError` keeps that true and fits the
  architecture better — the shape item 3 used for `Ellipsis`.
- `Error.kind()` answers the native name (`"ValueError"`); it should probably
  answer the POOP class once one exists.
- Whether the root should also inherit `Object`, giving user-defined exceptions
  `print()` / `class_name()`. Today `class MyError(Exception)` sits outside the
  `Object` tree entirely — verified: `MyError("x").class_name()` fails, because
  `ClassTransformer` only injects `Object` when a class declares no base.
  Untested.

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

### 8. The REPL renders errors worse than the file runner

`_format_error` (`poop/cli.py:16-30`) draws a gutter and caret; it is private to
`cli.py`. `poop/repl.py` prints `f"poop: {exc}"`. Same program, two surfaces:

```
file:  poop: print is forbidden — use obj.print() instead (line 4, col 8)
         4 |         print(x)
           |         ^
REPL:  poop: print is forbidden — use obj.print() instead (line 4, col 8)
```

The REPL — the primary learning surface — prints a line/col pointing into a
buffer that has already scrolled away, while holding the source in hand.

**Proposal**: hoist `_format_error` into a shared module and use it in both.
Also drop the useless `(line 1, col 0)` on single-line REPL input.

### 9. `:explain` denies the project's central doctrine

```
>>> :explain import
poop: nothing to explain about 'import' — it may simply be allowed.
```

`import` is banned, and with one of the best messages in the codebase ("POOP is
the language, not the library"). `_EXPLAIN_SNIPPETS` simply has no entry for
`import`, `invert` (`~x`), unary minus/plus, or `type_alias` — all banned — and
the fallback then asserts they may be allowed.

**Proposal**: add the missing entries, and reword the fallback so it stops
claiming an allowance it has not verified. Better still, derive `:explain` from
`DEFAULT_VALIDATORS` so the two cannot drift again.

### 10. One error per validator, in registration order

`make_node_validator` raises on first hit, aborting the visitor, and
`validate_all` catches one per validator. Verified: a file with three `if`s
reports exactly one — even under `--validators-only`, whose help text promises
"report all errors". The flag reports every *validator*, not every *occurrence*.
Migrating a real Python file becomes fix-one/rerun/repeat.

`--validators-only` also emits in `DEFAULT_VALIDATORS` order, not source order.
Verified on a file whose errors sit on lines 2, 3, 4, 5 — reported as 3, 5, 2, 4.

**Proposal**: sort `--validators-only` output by `(lineno, col_offset)` — trivial
— and let validators accumulate occurrences rather than raise on the first.

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
