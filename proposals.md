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

### 64. 158 of the 298 function-local imports break no cycle

`CONTRIBUTING.md`: "All imports live at the top of the module. Use a
function-local `import` only to break a circular import." `poop/` holds 298
function-local imports of its own modules. Building the module-level import
graph and asking, for each one, whether its target already reaches the
importing module, says 158 of them could be hoisted together without closing
a cycle. The sharpest cases import the module at the top *and* inside the
function:

```python
# poop/types/_iterable_mixin.py
from poop.types._argument import MISSING          # line 19, module level

    def do(self, block=MISSING):
        from poop.types._argument import a_block  # and again in map, filter,
                                                   # filter_false, find, reduce,
                                                   # all and any
```

`reduce` re-imports `MISSING` itself, shadowing the module-level name with the
same object. `bytes.py` has 21 such imports and none closes a cycle today;
`float.py` 16 and none; `string.py` 17 of 19. Sixteen modules also import
`to_boolean` at runtime at the top and then again under `if TYPE_CHECKING:`
(ruff `TC004`).

The 140 that remain are real, and concentrated: `meta.py` (44) and `object.py`
(39) sit under everything, so the root's protocol cannot name `Boolean` or
`Str` at import time. Those should stay — but only three sites in the whole
package say so (`# circular: block imports Object`), so a reader cannot tell a
load-bearing lazy import from a habitual one.

Two pairs are free one way only: `float → int` (12 sites) and `int → float`
(8) each hoist alone and form a cycle together, so the hoist is a set to pick,
not a search-and-replace.

**Fix.** Hoist the 158, drop the 16 duplicate `TYPE_CHECKING` imports, and turn
on ruff's `PLC0415` so each survivor carries a `# noqa: PLC0415` naming its
cycle. Trialled for `_iterable_mixin.py` (the eight `a_block` imports and
`_sorted`'s `a_key` hoisted): suite and `ty` pass. The per-call cost is small
but not zero — every `xs.do(…)` and `xs.map(…)` runs an import statement
before it does anything — and the rule in `CONTRIBUTING.md` would become one
the linter holds.

---

### 69. `repl.py` imports `readline` in three functions and tracks one registration in a global

`readline` is absent on one platform, and the module handles that three times:
`_setup_readline`, `_save_history` and `_readline_input` each open with their
own `try: import readline / except ImportError`. Whether history saving has
been registered is a module-level flag flipped through `global
_history_saver_registered`.

The same file writes to stdout two ways: `_OUT.print(...)` for values, headers
and the banner, and bare `print(...)` eight times — each with a `# noqa: T201`
for a rule the project does not enable (item 75) — for usage lines, `:help`,
and `:explain` output. The two paths wrap differently and only one of them is
the console the module's own comment says "decides per destination".

Smaller, same module: `_meta` dispatches three commands through `if`/`elif`;
`run` saves and restores `sys.displayhook` by hand around a 65-line loop;
`try: … except FileNotFoundError: pass` is `contextlib.suppress`.

**Fix.** One guarded import at the top (`try: import readline` / `except
ImportError: readline = None`), with the three functions testing the name. The
saver registers itself once behind `functools.cache` rather than a `global`.
Every write goes through `_OUT`. `_meta` becomes a `dict` of command → bound
method, and the displayhook swap a small `@contextmanager`, which also lets
`run`'s body be read without its `try`/`finally` frame.

---

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
