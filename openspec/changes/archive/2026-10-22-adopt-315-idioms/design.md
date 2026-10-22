# Design

## Context

See proposal.md — Why. Three facts shape the approach, all verified on the
pinned toolchain (Python 3.15.0, ruff 0.17.0, ty 0.0.87):

- ruff (check and format) and ty accept PEP 798 unpacking in list, set, dict
  and generator comprehensions, including a bare generator argument
  (`Counter(*src for src in sources)`).
- ty narrows a PEP 661 sentinel: for `b: int | MISSING = MISSING`, `b` is
  `int | MISSING` on entry, `MISSING` inside `if b is MISSING`, and `int`
  after it. It does **not** accept the marker in a union when it is declared
  `MISSING: Final = sentinel(...)` — the `Final` annotation hides the
  sentinel type — so the markers are declared bare.
- `re.Pattern.prefixmatch` exists on 3.15.0 and is `match` under its new
  name; no ruff rule flags `match` yet.

## Goals / Non-Goals

**Goals:**
- The interpreter's source uses 3.15's spelling where 3.15 gave one.
- The marker module keeps its three properties (identity, narrowing, named
  repr) with the builtin instead of imitating them.

**Non-Goals:**
- Any observable change. The markers' repr changes from `<missing>` to
  `MISSING`, but no test and no user-facing message carries it.
- Touching the `Sentinel` wrapper or the `sentinel` transformer.

## Decisions

- **Bare declarations, no `Final`.** `MISSING = sentinel("MISSING")` is what
  ty narrows on; a `Final` annotation breaks the union (verified). A
  sentinel is rebindable in principle, but so was the enum member; the
  module's leading underscore is the guard, as before.
- **The annotation is the marker.** `block: Block | MISSING = MISSING`
  replaces `block: Block | Missing = MISSING`, dropping the five type
  aliases. One name per marker, which is what PEP 661 designed `|` support
  for; the alternative — keeping `type Missing = ...` as an alias of the
  sentinel — is one more spelling of the same thing, the duplication the
  module docstring was written against.
- **Comprehension unpacking only where it removes a construct.** The six
  sites each lose a `chain.from_iterable`, a `list(...)` wrapper or a
  nested `for`. A comprehension that is a plain projection stays as it is;
  the rewrite is not a sweep for `for` clauses.
- **`prefixmatch` on the compiled patterns only.** The seven sites call
  `.match` on a module-level `re.compile(...)`; the rename is the method's.
  No `re.match(pattern, text)` module-level call exists.

## Risks / Trade-offs

- [ty's sentinel support is young] → The narrowing is verified on 0.0.87
  before the rewrite begins; `uv run ty check poop/ tests/` is the gate of
  the sentinel task, and a regression on a later ty is a Dependabot-style
  bump to test first (as the project already does for ty and ruff).
- [63 annotation sites for `Missing` alone] → A mechanical `sed`-able
  rename (`| Missing` → `| MISSING`, and the import lines), reviewed by ty
  and the full test suite, in one commit so the module and its importers
  never disagree.
- [`chain` import removal] → ruff's `F401` catches a leftover and `F821` a
  missing one; both are in the gate.
