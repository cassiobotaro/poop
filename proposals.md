# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 12–20 come from a pass over `poop/` for shape rather than types: what repeats, what a stdlib module already does, what a
library function changes about the process it runs in. Each was measured or
checked before being written down — the import-cycle idiom in 12 on Python
3.15, the overhead in 14 with `timeit`, the redundancy in 15 by walking every
class's MRO. Order: 13, 14, 15 are independent and small; 16 and 17 are the two
front-end items; 18 is independent; 19 is the maintainer's call; 20 is the
lock.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 21. Once every
item has been implemented and deleted, numbering starts over at 1.

### 13. `cloak` is a class keyword, and the mixins share one base

Every wrapper module ends with `cloak(Int, "int")`: 43 trailing calls, 13 of
them `cloak(_SomeMixin, "object")` under nine copies of the same four-line
comment ("Cloaked as `object`, the root's own spelling: these methods are
inherited by many wrappers…"). The cloak is part of the class's declaration —
the name it answers to — and the package already says so for one family:
`class BytesIterator(_IteratorBase[Int], name="bytes_iterator")` cloaks
through `_Cursor.__init_subclass__`, and `_DictView` does the same. The rest
of the tree spells it as a statement after the fact, which also means a new
wrapper can be defined and the line forgotten; `tests/test_cloak.py` exists to
catch exactly that.

The mixins carry a second repeated declaration: `__slots__ = ()` with the
same paragraph explaining that a slot-less class anywhere in an MRO restores
`__dict__` (`_value_eq.py`, `_iterable_mixin.py`, `_sequence.py`,
`_set_algebra.py`, `_bytes_like.py`, …).

**Fix.** `PoopMeta.__new__` takes `name: str | None = None` as a class
keyword and applies `cloak` when it is given; `Object`'s subclasses then read
`class Int(_NumericCompareMixin, Object, name="int")` and the trailing call
goes. `_Cursor` and `_DictView` stop redefining `__init_subclass__` for it. The
mixins — plain classes outside the `Object` tree — descend from one `_Mixin`
whose `__slots__ = ()` and `__init_subclass__` cloak as `object`, and whose
docstring holds the `__dict__` paragraph once. `cloak` itself stays a
function, since `builtin_alias` and the exception mirrors call it on classes
they build by hand.

### 14. The protocol-slot adapter wraps only a program's classes

`PoopMeta.__new__` wraps `__str__`, `__repr__`, `__bool__`, `__hash__` and
`__len__` in `_adapted` so a *program's* class can answer a `Str` or an `Int`
from them and CPython still receives a native. Its docstring says the library's
own wrappers "pass through untouched" — true of the value, not of the call:
every one of the 49 wrappers' five slots is wrapped too, and each `hash(x)`,
`str(x)`, `len(x)` or `bool(x)` on a POOP value pays a Python-level frame, an
`isinstance`, and a `functools.wraps` indirection to learn it was native all
along. Measured on `Int(1)`, 500k calls each:

| call | through `_adapted` | the slot itself |
|---|---|---|
| `hash(x)` | 0.29 s | 0.15 s |
| `str(x)` | 0.35 s | 0.19 s |

`hash` is on the path of every `Dict` and `Set` operation, `bool` of every
`if_true`, `len` of every `len()`. The two populations are already
distinguishable at class-creation time: the executor binds `__name__` to
`"__poop__"`, so a class a program defines arrives with
`namespace["__module__"] == "__poop__"`, and a library class with
`"poop.types.…"`.

**Fix.** Adapt the slots only when the namespace's `__module__` is
`"__poop__"`. The library's wrappers already answer natives, which is what the
short-circuit was checking at run time, class by class, call by call. One
test per slot that a library wrapper's slot is the function written in its
module, not a wrapper around it.

### 15. `__repr__ = __str__` is already `Object`'s answer

Twenty-two classes end their body with `__repr__ = __str__` — `Int`, `Float`,
`List`, `Dict`, `Set`, `Range`, `Slice`, `Try`, `With`, `NoneClass`, the
iterator base, … — and `Object.__repr__` is `return str(self)`. Walking every
class in `poop/types/` and asking what `__repr__` would resolve to without
the alias answers `Object.__repr__` for all twenty-two; the four classes whose
`__repr__` differs from `__str__` — `Object` itself, `Str`, `Boolean` and
`ByteArray` — define a real one and are unaffected. The alias is also what forces `_adapted` to wrap
each class's `__repr__` separately from its `__str__`, since both land in the
namespace.

**Fix.** Delete the twenty-two lines. Behaviour is identical: `repr(x)`
reaches `Object.__repr__`, which calls the class's own `__str__`.

### 16. The REPL is a `code.InteractiveConsole`

`Repl.run` (`repl.py`) re-implements the loop `code.InteractiveConsole`
ships: accumulate lines in a buffer, hand them to `codeop.compile_command`,
loop on `None` for an incomplete statement, reset on `SyntaxError`, switch the
prompt between `>>>` and `...`, swallow `KeyboardInterrupt` and end on
`EOFError`. Sixty lines of `run` plus `_indent_for`, `_readline_input` and the
`_leading_mark` flag are that loop; what is POOP's is the pipeline in
`run_source_repl`, the per-input filename, the `:meta` commands, the coloured
prompt, the auto-indent and the display hook. `InteractiveConsole` has an
override point for each: `raw_input` (prompt, indent hook, meta dispatch,
byte-order mark), `runsource` (the pipeline, the filename, the error report),
`write` (stderr through `_ERR`), and `sys.ps1` / `sys.ps2` for the prompts.

The module also keeps `_OUT = OUT` and `_ERR = ERR` as module globals "so a
test can swap the REPL's own", and `tests/test_repl.py` does so with
`monkeypatch.setattr("poop.repl._OUT", …)` five times. A seam that is a module
global is a seam every test shares; the Pythonic one is a constructor
parameter.

**Fix.** `class Repl(code.InteractiveConsole)` with the four overrides;
`Repl(interpreter, *, out: Console = OUT, err: Console = ERR)` and the
module-level `_print_value` / `_error` / `_say` become methods writing to
`self._out` / `self._err`. The tests pass consoles in instead of patching the
module. `_PoopCompleter` and the readline setup are untouched.

### 17. `execute` does not leave the recursion limit raised

`executor.execute` calls `sys.setrecursionlimit(6000)` when the current limit
is lower, and never restores it — "raised, not set", the comment says, so a
caller that asked for more keeps it. A library function that changes
process-wide interpreter state as a side effect of running a program is the
kind of thing Python spells as a context manager; the test suite imports
`execute` and so runs the rest of its own tests, and pytest itself, at the
raised limit after the first POOP program.

**Fix.** A `_recursion_budget()` context manager in `executor.py` that raises
the limit for the duration of `exec` and puts the previous value back, used
around the one `exec` call. The REPL already goes through `execute` per input,
so each input runs under the budget and the prompt returns to the process's
own. The "keeps a higher limit" rule holds within the block: the manager only
raises, never lowers.

### 18. The mirrors under their own names

`raise MIRRORS["TypeError"](…)` appears 120 times — 71 `TypeError`, 22
`ValueError`, six each of `RuntimeError` and `AttributeError`, and a handful of
others. A string key into a module-level dict is how a registry is read, not
how an exception is raised, and the spelling costs something at every site: the
key is a `Literal` the checker verifies but the reader cannot complete, and
`exceptions.py` itself needs `cast("MirrorName", native.__name__)` to write
into the same table. The mirrors are classes with fixed names, built once at
import; nothing about them is dynamic after that.

**Fix.** A `poop/types/mirrors.py` that binds each mirror under its own name
after `exceptions` has built the table — `TypeError = MIRRORS["TypeError"]`
and so on, sixteen lines under one `# noqa: A001` comment saying that the
mirror *is* POOP's `TypeError` — and call sites read `raise
mirrors.TypeError(…)`. `MIRRORS` stays for the two readers that are
table-shaped: `poop_class_of` and the `_at.py` helpers that take a
`MirrorName`.

### 19. The call-name validators are one table

Of the 71 validators, 38 are a `CallNameValidator`: a module of five lines
holding a class, a `forbidden = frozenset({"len"})` and a `message` (seven of
them ban a small family — `iter` and `next`, `exec` and `eval`, …). They
differ in two strings and share one visitor, one base, one parametrised test
(`tests/test_validators/test_call_name.py` already walks them as data), and one
consumer — the REPL's `:explain`, which reads `forbidden` back off each
instance through `getattr(validator, "forbidden", ())`.

**Fix.** A mapping in `_call_name.py`, a frozenset of names to its message,
and `DEFAULT_VALIDATORS` extended with one `CallNameValidator(names, message)`
per row — so `len(DEFAULT_VALIDATORS)`, which `tests/test_doc_counts.py` reads
against `README.md`, counts as it does now. The 33 validators with a visitor
of their own keep their modules. `:explain` asks
`isinstance(validator, CallNameValidator)` instead of duck-typing the
attribute. `CONTRIBUTING.md`'s "a new validator" recipe gains a first step: a
banned builtin is a row, not a module. This one is a judgment call about
discoverability — `no_len.py` is a filename a reader can `ls` for — which is
why it is written down rather than done.

### 20. Turn on the rules the code already passes

Run with ruff's full rule set, `poop/` trips almost nothing outside the
families already on: `PERF`, `PIE`, `RET`, `PTH`, `C4` and `SIM` pass clean,
`FURB` and `PLR` in preview find five lines (three generator expressions that
are `itertools.starmap` — `errors.py:252`, `dict_items.py:24,56` — and two
`in (…)` tuples that are set literals — `errors.py:140`, `_argument.py:269`),
and `ARG`, `TRY`, `A`, `N` and `PLR` find two dozen sites that are each
intentional: a
`reversed` / `abs` / `round` *message* shadowing the builtin it replaces, an
unused `start` on `Str.sum` whose job is to refuse, an unused `other` on the
Boolean singletons' operators, `MessageNotUnderstood` without an `Error`
suffix.

**Fix.** Fix the five preview findings. Add `PERF`, `PIE`, `RET`, `PTH`,
`C4`, `FURB`, `ARG`, `TRY` and `PL` to `select`, ignore `A003` for the
message names that mirror builtins by design and `N818` for the one class, and
mark the remaining intentional sites with a `noqa` and the reason, as the
`PLW1641` sites do today. `RUF100` keeps each one honest.
