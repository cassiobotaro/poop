# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 1–7 come from reading [What's New in Python
3.15](https://docs.python.org/3.15/whatsnew/3.15.html) the day the project
moved to it. Everything 3.15 adds to the *syntax* already meets an existing
ban — `lazy import` is a flag on the two import nodes, comprehension
unpacking is a `Starred` inside the four comprehension nodes, and `match`
grew unary plus in a statement `no_match` refuses whole — so the items below
are about what 3.15 added to the *builtins* and to its own error messages.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 8. Once every
item has been implemented and deleted, numbering starts over at 1.

### 1. `frozendict` is a builtin now, and POOP has no `FrozenDict`

PEP 814 adds `frozendict` to the builtins: immutable, hashable when its
contents are, not a `dict` subclass, insertion-ordered but order-blind for
`==`. `INFECTIONS.md` opens with "every basic type has a POOP equivalent" and
lists `frozenset` → `FrozenSet`; `frozendict` is now the half-pair. Today
`frozendict({"a": 1})` answers `NameError: name 'frozendict' is not defined`
(the allow-list in `poop/executor.py` withholds it), which is correct and
teaches nothing.

**Fix.** A `FrozenDict` wrapper (`poop/types/frozen_dict.py`) and a
`FrozenDictTransformer` rewriting `frozendict(...)` the way
`FrozenSetTransformer` rewrites `frozenset(...)`. `RESERVED_NAMES` is derived
from the rewriters, so `no_builtin_shadow` reserves the name without a second
list. It is the `Dict` read surface (`at`, `get`, `keys`, `values`, `items`,
`len`, `includes`, `do`, `map`, …) without `at_put`/`update`/`pop`/`clear`,
answers `hash`, and `|` with a `Dict` or another `FrozenDict` answers a
`FrozenDict`, as CPython does. The dict views (`DictKeys`, `DictItems`) should
accept it on the set-algebra side like any other collection. Decide and write
down its relation to `MappingProxy`: a proxy is a live read-only *view* of a
`Dict`, a `FrozenDict` is a *value* — both exist in CPython, and the catalog
should say why POOP keeps both rather than folding one into the other.

### 2. `sentinel` is a builtin now — wrap it, or refuse it with a substitute

PEP 661 adds `sentinel("MISSING")`: a unique object whose `repr` is its name
and whose identity survives copying. It answers the same bare `NameError` as
item 1. Two readings, and the catalog should pick one:

- **Refuse.** `sentinel(...)` is a free function, and the Smalltalk idiom for a
  unique marker is `Object new` held in a variable — in POOP,
  `MISSING = Object()` and `x.is_identical(MISSING)` already work. A
  `CallNameValidator` `no_sentinel` with that substitute makes `:explain
  sentinel` answer something, which is the rule for activating a validator.
- **Wrap.** A `Sentinel` type whose `__repr__` is its name is twenty lines, and
  the name-as-repr is the only thing `Object()` lacks.

Recommendation: refuse. POOP keeps the one root a program can name, and a
named marker is a class of its own (`class Missing(Object): pass`) — which
also gives it a `class_name()`. If "wrap" wins, note that `_sentinel.py`
already exists under `poop/types/` for an internal marker and must not be
confused with the user-facing one.

### 3. A withheld builtin answers the same `NameError` as a typo

`copyright.print()`, `NotImplemented.print()`, `frozendict(…)`,
`sentinel(…)` and now `ImportCycleError` all answer `name 'x' is not
defined` — the sentence a misspelt variable gets. Before 3.15 the withheld
names were ones nobody reached for; `frozendict` and `sentinel` are the first
two a Python programmer will type on purpose, and the message does not say
that POOP *chose* not to offer them.

**Fix.** Where `poop_message` (`poop/types/_message.py`) rewords CPython's
sentences, a `NameError` whose `.name` is in `builtins` but not in
`_ALLOWED_BUILTINS` reads `'sentinel' is a Python builtin POOP does not offer`
— followed by the substitute when a validator or a proposal names one
(`frozendict` → item 1, `sentinel` → item 2), and by `try :explain` otherwise.
`:explain <name>` for such a name should answer the same sentence instead of
"it may simply be allowed". Derive the set from `builtins` minus the
allow-list, not from a table — the table is what fell behind for `:explain`
once already.

### 7. `Boolean.bit_invert` keeps a behaviour CPython is removing

3.15 deprecates `~True` for removal in 3.16, with the warning: "This returns
the bitwise inversion of the underlying int object and is usually not what
you expect from negating a bool. Use the 'not' operator for boolean negation
or ~int(x) if you really want the bitwise inversion". `Boolean.bit_invert`
(`poop/types/boolean.py`) is that exact behaviour — `True.bit_invert()`
answers `-2` through `_as_int()` — and because it never calls `~` on a `bool`,
it will keep answering `-2` after 3.16 removes it.

**Fix.** Refuse it in step with CPython: `bool does not understand
#bit_invert — send #not_, or #bit_invert to int(b)`, which is CPython's own
advice in POOP's vocabulary. Remove the method rather than warn: POOP has no
warnings channel, and the catalog already argues that a refusal with a
substitute teaches where a silent answer does not. The other `Boolean`
delegations to `int` (`abs`, `bit_length`, `bit_count`, `negated`, arithmetic)
stay — CPython keeps those.
