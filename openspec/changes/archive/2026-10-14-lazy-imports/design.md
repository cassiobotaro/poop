# Design

## Context

See proposal.md - Why. What the approach rests on, verified on the tree and
on the installed 3.15.0:

- `lazy import` / `lazy from ... import ...` is module-level only: a
  `SyntaxError` inside a function, a class body, a `try`, or with `*`. An
  alias (`lazy from x import y as z`) is allowed.
- Resolution happens on first use of the name, including a read through
  `vars(module)`, `getattr`, or an annotation evaluated by `annotationlib`;
  after that the module global holds the real object.
- The cycles in `poop/types` are of one shape: a hub (`object`, `meta`,
  `boolean`, `none`, `string`, `block`, `float`, `_bridge`) is needed at
  class-definition time by modules it would import, so it defers those
  imports into method bodies. Every such site has a `# circular:` comment and
  a `# noqa: PLC0415`.
- `hot-path-imports` added `late(module, name)` (a cached getter, ~70 ns per
  call) at 17 hot sites and a module global `_METHOD_BLOCK` that `block.py`
  installs into `_descriptor.py` for the single hottest site.
- `tests/test_hot_paths_bind_late.py` records every `poop/`-internal import
  fired from inside a function while a fixed set of operations runs.
- Baseline, best of five, 20 000 iterations: `(5).abs()` 2404 ns, `a._value`
  200, `Int(3)` 483, `Int + Int` 1713, `Int < Int` 1547, `xs.map(block)` 2889
  (from `object-hooks-off-the-hot-path`'s *Measured*).

## Goals / Non-Goals

**Goals:**
- No function-local import of a `poop` module anywhere under `poop/`; ruff's
  `PLC0415` enforces it with no exemptions.
- One mechanism for deferred imports, the language's.
- No behavior change and no performance regression; a small gain where the
  getter and the cold local imports were.

**Non-Goals:**
- Converting `if TYPE_CHECKING:` imports (phase 2).
- Reordering or hoisting any eager import.
- Changing which module is imported where: the graph of edges stays, only
  the spelling of the deferred ones changes.

## Decisions

**1. Mechanical lift, one rule.** Every `from poop... import ...` whose
enclosing scope is a function (or method) becomes a `lazy from` at module
level, after the last eager import and before the `TYPE_CHECKING` block,
deduplicated per module, carrying the `# circular:` comment of the site it
came from (the first one when several sites imported the same name). A
one-off script does the lift (AST finds the sites; text edits move them),
`ruff check --fix` and `ruff format` settle the import block, and the diff is
reviewed file by file. *Alternative*: convert by hand. Rejected: 272 sites,
and a mechanical rule is the thing that keeps "no eager import became lazy"
true.

**2. The `# circular:` comment stays on the lazy line.** `lazy` is a claim
that deferring is safe and needed; the comment says why. A later reader who
sees `lazy from poop.types.float import Float` without the comment cannot
tell whether it may be made eager. *Alternative*: drop the comments as noise.
Rejected for the reason above.

**3. A name imported both lazily (runtime) and under `TYPE_CHECKING`
(annotations) keeps only the lazy import.** The lazy name resolves in
annotations through `annotationlib` as the typing-only one did, and two
imports of one name in one module is the kind of thing ruff's `F811`/`TC`
rules exist to catch. Names used *only* in annotations stay under
`TYPE_CHECKING` (phase 2 decides their fate).

**4. `_late.py` goes, `_METHOD_BLOCK` goes.** Each `_x = late("m", "N")`
becomes `lazy from m import N` and the call sites `_x()` become `N`. In
`_descriptor.py`, `lazy from poop.types.block import _MethodBlock` replaces
the getter, the global and the installer; the first message send resolves it
and every later one reads a global (measured 30 ns, below the installed
global's own cost once the `None` test is counted). `block.py` loses the
install line. *Alternative*: keep `late()` for symmetry with the design that
introduced it. Rejected: it was a stand-in for a language feature the
interpreter now has, and its docstring already named the global as the
faster shape.

**5. The guard runs the examples.** The recorder test keeps its hot
operations and adds one test that runs every program under `examples/` (the
same set the import ranking used) with the recorder armed and asserts the
record is empty. With `PLC0415` strict this is belt and braces: ruff catches
the spelling, the test catches an import fired through `exec`, a transformer
or a path ruff does not see.

**6. Measurement is recorded, with a no-regression gate.** The same twelve
operations as the last two changes, before and after, same session. The gate
is "no operation slower by more than 5 %"; the expected gain is small (the
getter's 40 ns per use and the cold sites), and the point of this change is
the code, not the clock.

## Risks / Trade-offs

- [A deferred import that was deferred for a reason other than a cycle — e.g.
  to avoid import-time cost of an optional module] → none found: every
  function-local `poop` import carries a `# circular:` comment; a site
  without one is reviewed before lifting.
- [An import that must run at a *specific moment* (side effects on import)]
  → `poop/types` modules have no import-time side effects beyond class
  creation and `cloak`; `block.py`'s `install_method_block` was the one, and
  it is removed by this change.
- [ruff's isort groups `lazy` imports and reformats the import blocks] →
  accepted; `ruff format` is run after the lift and the hooks keep it.
- [An `ImportError` moves from startup to first use] → the suite and the
  examples exercise every lazy edge; `tests/test_no_local_imports.py` runs
  the examples under the recorder, so a broken edge fails there.
- [coverage.py or pytest on 3.15 mishandle the `lazy` opcode] → the first
  lifted module is run under the full gate before the rest are lifted.
- [Phase 2 pressure: with `lazy` available, `TYPE_CHECKING` looks redundant]
  → named out of scope; `CONTRIBUTING` states both rules side by side.

## Measured

Before is `main` at `8589c59` in a temporary worktree, after is the lifted
tree; the two ran interleaved for two rounds in one session, and the table
takes the best of the two rounds on each side (ns/op, best of five runs of
20 000 iterations inside each round).

| Operation | Before | After | Change |
|---|---|---|---|
| `(5).abs()` | 2546 | 2434 | -4 % |
| `a._value` | 199 | 200 | 0 % |
| `Int(3)` | 534 | 500 | -6 % |
| `Int + Int` | 1961 | 1563 | -20 % |
| `Int < Int` | 1619 | 1528 | -6 % |
| `Int == Int` | 1247 | 1188 | -5 % |
| `Int * Float` | 2281 | 1994 | -13 % |
| `an_int(Int)` | 923 | 938 | +2 % |
| `List.at` | 3188 | 3100 | -3 % |
| `Str.len` | 2701 | 2480 | -8 % |
| `true.if_true` | 1974 | 1828 | -7 % |
| `xs.map(block)` | 3488 | 2962 | -15 % |

The gate held: nothing slower by more than 5 % (the one plus is within the
round-to-round noise of ~5 %). The gains sit where the cold local imports and
the getters were: arithmetic (`_arith`'s getter, `to_poop`), `map` (the
`_iterable_mixin` getters), `Str.len`.

Found during apply: the first version of the lifting script carried *every*
comment block above a function-local import into the import block, including
comments that explained the method's code; it now carries only a block that
mentions the import or the cycle. The inventory counted in the proposal (272)
included imports inside `if TYPE_CHECKING:` blocks nested in functions; the
function-local imports proper were 125 (72 in `object.py`/`meta.py`, 53 in the
other type modules, none elsewhere), and all are lifted.
