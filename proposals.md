# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Items 62–75 come from one review of `poop/` as Python code rather than as a
language: what a Python engineer would change about how the interpreter is
written. Two of them (62, 63) turned out to be behaviour, and lead for that
reason; the rest are ordered roughly by how much code each one touches.

When an item is implemented, delete its entry from this file — no `DONE`
marker and no summary left behind. The decision and its reasoning belong in
[`INFECTIONS.md`](INFECTIONS.md), and the diff lives in the git history.

Numbering continues while the backlog has open items; the next one is 76.
Once every item has been implemented and deleted, numbering starts over at 1.

### 75. Twenty-four `noqa` directives silence rules that are not enabled

`pyproject.toml` selects `E4`, `E7`, `E9`, `W`, `F`, `UP`, `I`, `C90`, `S`,
`ANN`, `PYI`. The code suppresses rules outside that set: `# noqa: T201`
eleven times, `BLE001` four, `N801` three, `PERF203` two, and `TRY301`,
`B015`, `PLR1702`, `PLR2004` once each across `poop/` and `tests/` — 24
directives, plus one `C901` that is enabled and no longer fires, by `ruff
check --extend-select RUF100`. Each records that someone considered the rule
and judged the line fine; none of those rules runs, so nothing checks the
lines that carry no comment.

Running the wider set over `poop/` says what it would have caught:

- `PLW1641` (`__eq__` without `__hash__`) — eight classes, four of them item
  62's bug.
- `PLC0415` (import outside top level) — item 64.
- `B905` — five `zip()` calls without `strict=`. Four are fine as they are;
  `_poop_dict_from_pairs` pairs its arguments with `zip(it, it)`, which drops
  an odd trailing element in silence where `itertools.batched(pairs, 2,
  strict=True)` would refuse.
- `RUF022` / `RUF023` — `poop.types.__all__` and four `__slots__` unsorted.
- `SIM102` / `SIM105` — two collapsible `if`s, one `contextlib.suppress`.
- `TC004` — the sixteen duplicate `to_boolean` imports of item 64.

One modernisation belongs with it: 24 of the 187 modules open with `from
__future__ import annotations`. On the required 3.14, annotations are already
evaluated lazily (PEP 649), so the import is redundant, and the other 163
modules show the package runs without it.

**Fix.** Add `B`, `SIM`, `BLE`, `T20`, `PLC0415`, `PLW1641` and `RUF` (for
`RUF100`, which keeps suppressions honest from then on) to `select`, fix or
annotate what they report, and delete the directives for rules the project
decides not to adopt. `N801` is the one to leave off deliberately: `class_side`
is lowercase because it is used as a decorator, and the three comments saying
so can become one line in the config.
