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
