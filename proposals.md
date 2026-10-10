# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 12–20 come from a pass over `poop/` for shape rather than types: what repeats, what a stdlib module already does, what a
library function changes about the process it runs in. Each was measured or
checked before being written down — the import-cycle idiom in 12 on Python
3.15, the overhead in 14 with `timeit`, the redundancy in 15 by walking every
class's MRO. Order: 19 is the maintainer's call; 20 is the lock.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues from the highest open item; the next one is 21. Once every
item has been implemented and deleted, numbering starts over at 1.

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
