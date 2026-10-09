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

Numbering continues from the highest open item; the next one is 9. Once every
item has been implemented and deleted, numbering starts over at 1.

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

### 8. A class-side operator names `_AliasMeta`

Found while wrapping `sentinel`: `int | sentinel("M")` answers `TypeError:
_AliasMeta does not understand #| with a sentinel`. A bare builtin name is the
alias class (`poop/types/_alias.py`), and `type.__or__` — CPython's union
builder, so `int | str` quietly answers a `types.UnionType` POOP has no use
for — declines a non-type operand, after which `poop_message` rewords
CPython's `unsupported operand type(s) for |: '_AliasMeta' and 'sentinel'`
with the metaclass's name in the receiver slot. `receiver_label` already
exists so `does not understand` says `int` for a class receiver; the operator
path does not go through it.

**Fix.** Decide what a class-side `|` means in POOP — probably nothing, since
unions belong to annotations the language does not write — and refuse it
under the class's own name (`int does not understand #| with a sentinel`),
which also closes the silent `int | str` success. The wording sweep's operator
half pairs instances only; a class receiver in `_OPERANDS` would have found
this.
