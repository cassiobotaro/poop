# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Every claim below was verified by running the interpreter; the quoted output is real.

---

## Object leaks

Surfaces that hand a raw Python object — or a POOP-internal identity — to user
code, against *"all POOP methods return POOP types"* and *"`_poop_*` must never
reach user-visible output"*. Each is one guard or one identity patch from closed;
the open question in every case is a naming/semantics decision, not a mechanism.

### 1. POOP class objects render as CPython's `<class '...'>`

`PoopMeta` cloaks only the *direct-message* path: `name`, `repr`, `ascii`,
`print`, `format` are all class-side POOP methods, but the metaclass defines no
native `__repr__`/`__str__`. So the moment a POOP class object is rendered
through Python's own `repr()`/`str()` — which every collection's `__str__` does,
joining on `repr(element)` — it falls through to `type`'s default and answers
Python's `<class '...'>` vocabulary inside a POOP message. The same object then
renders two different ways depending on nesting:

```
(5).class_().print()          ->  int                # direct message: clean
[(5).class_()].print()        ->  <class 'int'>      # nested in a List: leak

class Foo(Object): pass
Foo.print()                   ->  Foo                # direct message: clean
[Foo].print()                 ->  <class 'Foo'>      # leak
[Object].print()              ->  <class 'object'>   # leak
```

This hits **every** POOP class — arbitrary user classes and even the fully
cloaked builtin/exception mirrors — because the leak is the *rendering form*
(`<class '...'>`), not the name inside it. `PoopMeta.repr`'s own docstring names
exactly this hazard ("would put Python's vocabulary inside a POOP message's
answer"), yet the native path bypasses that method entirely.

**Uncloaked classes additionally leak their module path.** `Block`, `Error`,
`Try`, `With` never patch `__module__`/`__name__`, so their native `repr` shows
the full internal path rather than a builtin name:

```
repr(Int)    ->  <class 'int'>                       # patched wrapper
repr(Block)  ->  <class 'poop.types.block.Block'>    # leak
repr(Try)    ->  <class 'poop.types.try_.Try'>       # leak
repr(Error)  ->  <class 'poop.types.error.Error'>    # leak
repr(With)   ->  <class 'poop.types.with_.With'>     # leak
```

**Decision needed:** add a `PoopMeta.__repr__`/`__str__` (returning
`cls.__name__`, or a POOP-appropriate rendering) so nested class objects answer
in POOP's vocabulary — this closes both symptoms at the root — and patch
`__module__`/`__name__` on the four uncloaked classes so their name is
Python-facing (`Try`/`With` keep their name via `__module__ = "builtins"`;
`Block`/`Error` also need a name chosen, see item 2).

### 2. `class_name()` leaks the internal wrapper name

For the uncloaked classes the name a POOP object answers about itself is the
wrapper's, not anything a Python programmer would recognise. Verified through the
full pipeline:

```
# a stored lambda
b = (lambda: 1)
b.class_name().print()                                      ->  Block

# a caught exception, inside an except_ handler
Try(lambda: [].pop()).except_(IndexError,
    lambda e: e.class_name().print()).run()                 ->  Error
```

`Block` is a name the user should never see; CPython answers `function` for a
lambda. `Error` masks the real exception — `e.kind()` already answers the
exception's POOP class, so `e.class_name()` returning `Error` is the same
name-for-a-class substitution `Error.kind`'s own docstring warns against. The
`:methods <lambda>` REPL header (`repl.py`) reuses `type(obj).__name__` and so
prints `Block understands …` for the same reason.

`Try`/`With` answer their own legitimate names, so only `Block` and `Error` leak
here — and both need a **name** chosen, which is why this is a proposal and not a
mechanical patch.

**Decision needed:** what identity should `Block` and `Error` answer
(`function`? the wrapped exception's name?)? Once chosen, set `__name__` to match
so `class_name()`, the `:methods` header, and item 1's rendering all agree — the
uncloaked-class patch is shared with item 1.

### 3. `dir()` leaks a `_poop_*` name and every private internal

`Object.dir()` and `PoopMeta.dir()` return `builtins.dir(self)` unfiltered, so
the introspection substitute exposes exactly the names the mangling scheme
exists to hide:

```
{1: 2}.items().dir().includes("_poop_own_set").print()      ->  True
```

`_poop_own_set` (`dict_items.py`) is a `_poop_*`-named method reaching
user-visible output — a direct violation of the namespace-hygiene rule. Alongside
it, `dir()` lists every `_`-prefixed internal (`_dict`, `_iter_items`,
`_reject_dunder`, `_value`, `_items`, …). `:methods` already filters
`_`-prefixed names (`repl.py`); `dir()` does not.

**Decision needed:** should `dir()` filter `_`-prefixed / `_poop_*` names to
match `:methods` (diverging from CPython's `dir()`, which shows everything), or
is exposing them acceptable and only the `_poop_*` binding needs renaming? The
tension is that CPython's own `dir()` is deliberately exhaustive, so filtering is
a POOP choice, not a bug fix.

### 4. `get_attr` returns the raw Python primitive behind any private attribute

`Object.get_attr` / `PoopMeta.get_attr` (POOP's sanctioned substitute for the
banned `getattr`) guard only against dunders via `_reject_dunder`. A
single-underscore private slips through and hands back the unwrapped `_value` —
a naked Python object in user code:

```
(42).get_attr("_value")             # -> raw Python int
    .print()                        # -> 'int' object has no attribute 'print'

[1, 2, 3].get_attr("_items")        # -> raw Python list
    .class_name()                   # -> 'list' object has no attribute 'class_name'
```

This is the single-underscore twin of closed proposal *"Dunder attribute access
reproduces banned builtins verbatim"*: that item closed the `__dunder__`
spelling through `_reject_dunder`, but `_value`/`_items`/`_data`/`_fn` were never
in scope, so the same raw-primitive leak stays open one underscore down.
`has_attr`/`set_attr`/`del_attr` share the blind spot (`set_attr("_value", …)`
pokes wrapper state directly). Class-side `has_attr` (`meta.py`) additionally
skips `_reject_dunder` entirely, unlike its instance-side twin.

**Decision needed:** extend the guard to reject the wrapper's own private state
(`_value` and the `_*` slots) — diverging from CPython, where `getattr(obj,
"_value")` is merely a convention violation, not an error — or accept that a user
who names a private has left the POOP contract on purpose. Either way, align
class-side `has_attr` with the instance-side guard.
