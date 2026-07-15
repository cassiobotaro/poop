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
first that does not, and that is deliberate. Item 2's open question (raw dunder
calls) is the next place the same trade-off surfaces.

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

**Proposal**: a `no_dunder_attribute` validator rejecting `__dict__`,
`__class__`, `__mro__`, `__bases__` in `ast.Attribute` position.
**Substitute**: `x.class_name()` or polymorphism; for `__dict__`, none — the
ban is the decision, exactly as `no_introspection` already argues for `vars`.

Open question: whether to extend it to raw dunder *calls* (`x.__len__()`,
`(5).__abs__()`, `col.__contains__(x)`). These defeat `no_len`/`no_abs`/`no_in`
and return raw primitives, but they pass the "does it look like an object
receiving a message?" test. A judgment call for the maintainer, not an obvious
bug.

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

---

## Error reporting and the REPL

The error machinery is sound and should be credited: `__module__`/`__name__`
masking plus `_user_lineno`'s frame-walk mean no `_poop_*` name, transformer
frame, or Python traceback ever reaches the user, and the reported line is the
deepest *user* frame. The gaps are in what is thrown away on the way out.

### 7. `ExecutionError` destroys the exception class name

`poop/executor.py:50` does `raise ExecutionError(str(exc), ...)`. `str(exc)`
drops the type:

| POOP shows | Real type |
|---|---|
| `poop: 'zzz' (line 2)` | `KeyError` |
| `poop: bad input (line 1)` | `ValueError` |
| `poop: x must be big (line 2)` | `AssertionError` |

`d.at("zzz")` on a missing key renders as literally `poop: 'zzz'` — a bare quoted
string with no hint that a key was missing. Worse, a learner writing
`Try(...).except_(ValueError, ...)` cannot see which class escaped.

**Proposal**: `f"{type(exc).__name__}: {exc}"`. Type names are already masked to
builtins, so this leaks no internals.

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

### 11. `INFECTIONS.md` contradicts itself on `help`

`help` is listed under **Active infections** ("No `help`", line 418) *and* under
**Explicitly allowed** ("Allowed.", line 567). Reality: `NoHelpValidator` is in
`DEFAULT_VALIDATORS` and `help(5)` is rejected. The *Explicitly allowed* entry is
stale and should be removed.

---

## Considered and rejected

- **stdlib mirrors of any kind** — settled: POOP is the language, not the
  library.
- **Cascades (`;`) and `yourself`** — Smalltalk-shaped, but they substitute no
  forbidden construct, which is the bar a new message has to clear.
- **`%` / `.format()`** — already the sanctioned surface replacing f-strings.
- **`@property` / `super()` / `+=` / binary operators** — explicitly allowed by
  design, with stated rationale.
