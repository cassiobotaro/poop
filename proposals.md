# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — substitute exists with a different name

Items where the substitute works, but the method name does not mirror the builtin. Implementing them is optional — depends on whether mirrored names take priority over a leaner API.

### 1. `slice()` → add a `.slice(start, stop, step)` alias?

**Today:** `poop/types/list.py:42`, `poop/types/tuple.py:37`, `poop/types/string.py:50`, `poop/types/bytes.py:36`, `poop/types/byte_array.py:30`, `poop/types/range.py:32` — all expose `copy_from_to(start, stop, step)`. Documented at `INFECTIONS.md:281`.

**Decision:** keep only `copy_from_to`, or add `.slice(...)` as an alias to align with the builtin name?

### 2. `enumerate(col)` → `col.enumerate()` returning a lazy `Enumerate` object?

**Suggested location:** `poop/types/enumerate.py` (new) plus a hook on `poop/types/_iterable_mixin.py` so every collection (`List`, `Tuple`, `Set`, `Range`, `Bytes`, `ByteArray`) inherits `.enumerate()`.

**Today:** `INFECTIONS.md:287` points to `col.map(block)` / `col.reduce(init, block)` with manual indexing.

**Two possible shapes:**

- **(a) Eager `List` of `Tuple(Int(index), item)`.** Cheap (~5 lines on `_IterableMixin`), matches every other collection method (`map`, `filter`, `reduce` are all eager). Materializes the whole list upfront — wasteful on large inputs.
- **(b) Lazy `Enumerate(Object)` object — preferred.** Mirrors Python's `enumerate` semantics 1:1: an iterator that yields `Tuple(Int(index), item)` on demand. Memory-efficient, single-pass, chainable.

**Why (b) is the preferred direction:** matches the user's mental model of `enumerate`, scales to large inputs, and unlocks the same lazy pattern for `zip` (item 3), `map`, `filter`, etc. as a future evolution.

**Why it is gated:** today POOP has **no** user-facing iterator type. The only interaction with iteration is `col.do(block)`; `next()` is banned by `no_iter`; there is no `Iterator` Object. Introducing a single lazy `Enumerate` in isolation would be the only lazy first-class object in the language, with no `next` substitute and only `do(block)` as a useful method — collapsing back to eager behavior on first use.

**Dependency:** **proposal 4** (first-class `Iterator` type). Decide that one first; lazy `Enumerate` falls out naturally as a specific iterator. If proposal 4 is rejected, fall back to shape (a).

**Sketch (assuming proposal 4 is accepted):**

```python
# poop/types/enumerate.py
class Enumerate(Iterator):  # Iterator base from proposal 4
    __slots__ = ("_source", "_start")

    def __init__(self, source: _IterableMixin, start: Int = Int(0)) -> None:
        self._source = source
        self._start = start

    def __iter__(self) -> Iterator[Tuple]:
        return (
            Tuple(Int(i), item)
            for i, item in _builtins.enumerate(self._source, self._start._value)
        )
```

Then `_IterableMixin.enumerate(start=Int(0)) -> Enumerate` — and because `Enumerate` is an `Iterator`, methods like `do`, `map`, `filter` work uniformly.

**Effort:** small once proposal 4 lands (~30 lines + tests). Without proposal 4: medium and inconsistent (one-off lazy type).

**Decision:** confirm shape (b) lazy `Enumerate` as the target, conditional on proposal 4? Otherwise fall back to shape (a) eager `List`.

### 3. `zip(a, b)` → `a.zip(other)` returning a lazy `Zip` object?

Same dependency tree as item 2: prefer a lazy `Zip(Object)` mirroring Python's `zip` (single-pass, stops at shortest), conditional on proposal 4. Fallback eager shape returns a `List` of `Tuple(item_a, item_b)`.

**Suggested location:** `poop/types/zip.py` (new) plus a hook on `poop/types/_iterable_mixin.py` accepting another iterable.

**Decision:** confirm the lazy shape conditional on proposal 4, with eager `List` fallback otherwise.

### 4. `iter(col)` / `next(it)` → first-class `Iterator` type?

**Today:** iteration only via `col.do(block)` (`INFECTIONS.md:294`).

**Implementation:** invasive — requires a new `Iterator` type in `poop/types/` plus a matching transformer in `poop/transformers/` (just like `Block` has its own).

**Decision:** introduce a first-class iterator, or keep the pure Smalltalk model (only `do`)?

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### 5. `setattr(obj, name, val)` → `obj.set_attr(name, val)`?

**Current asymmetry:** `Object` exposes `get_attr` (`poop/types/object.py:84`) and `has_attr` (`poop/types/object.py:87`) but no `set_attr`. `INFECTIONS.md:299-304` only says "use class methods", which is no longer the rule for `getattr`/`hasattr`.

**Decision:** complete the trio with `set_attr` (and a symmetric `del_attr`, item 6)?

### 6. `delattr(obj, name)` → `obj.del_attr(name)`?

Counterpart of item 5. Same symmetry argument.

### 7. `vars(obj)` → `obj.vars()` returning a `Dict`?

**Today:** bundled into `no_introspection` (`poop/validators/no_introspection.py`, `INFECTIONS.md:312`) alongside `globals()`/`locals()`.

**Important distinction:** `vars(obj)` on an instance returns `__dict__` — that is **instance state**, not lexical scope. POOP uses `__slots__`, so the natural substitute would iterate the slots and produce a `Dict[Str, Object]`.

`globals()`/`locals()` remain without a substitute (they are real lexical scope).

**Decision:** split `vars` out of `no_introspection` and give `Object` a `vars()` substitute?

### 8. `input(prompt)` → introduce a `Console` / `Stdin` type?

**Today:** `INFECTIONS.md:343-345` declares "interactive I/O — no POOP equivalent".

**Note:** Smalltalk *does* model interactive I/O (`Transcript`, etc.). Natural substitute: a POOP `Console` object with `Console.read_line(prompt: Str) -> Str`.

**Scope:** large — a brand new I/O subsystem.

**Decision:** worth the investment, or keep banned?

### 9. `open(path)` → POOP `Path` type inspired by `pathlib`?

**Today:** `INFECTIONS.md:349-351` declares "file I/O — no POOP equivalent".

**Important observation:** the stdlib's `pathlib` is already **object-oriented** — `Path("foo.txt").read_text()`, `Path("dir").iterdir()`, `Path("a").exists()`. The API matches POOP's message-passing model naturally, sparing us a "from-scratch subsystem".

**Possible models:**
- **(a) Wrapper around `pathlib.Path`** — a POOP `Path` wraps `pathlib.Path` and exposes methods like `read_text() -> Str`, `read_lines() -> List[Str]`, `write_text(content: Str) -> Path`, `exists() -> Boolean`, `iterdir() -> List[Path]`. Cheaper, leverages tested pathlib.
- **(b) `Str.open(mode)` returning a POOP `File`** — alternative originally proposed, closer to the builtin `open()` but requires designing the lifecycle from scratch (`close`, context manager via `With`).

**Recommendation:** (a). Pathlib has already done the work of "OO-ifying" filesystem I/O; POOP inherits it almost for free. For `open()` itself, `Path("foo").read_text()` / `write_text()` covers most uses without exposing open file handles.

**Suggested location:** `poop/types/path.py` (new) plus a transformer at `poop/transformers/path.py` to intercept `open(...)` and rewrite it to `Path(...).read_text()` when the pattern is obvious (or simply require users to write `Path("foo").read_text()` directly).

**Scope:** smaller than reimplementing I/O from scratch — wrapper over `pathlib` plus delegating methods.

**Decision:** adopt approach (a) with `pathlib` as the foundation, design `File` from scratch, or keep banned?

---

## Open decisions — language semantics

### 10. Smalltalk-style binary operator evaluation (left-to-right, no precedence)?

**Today:** Python evaluates `3 + 1 * 2` as `3 + (1 * 2) = 5` (precedence: `*` before `+`). POOP inherits that because the parser is Python's (`poop/parser.py` → `ast.parse`).

**In Smalltalk:** binary messages are evaluated **left-to-right with no precedence**. `3 + 1 * 2` reads as "send `+ 1` to `3`, then `* 2` to the result" → `(3 + 1) * 2 = 8`. It is a direct consequence of the principle "everything is a message to an object".

**Tension between POOP principles:**
- `INFECTIONS.md:8` — "Everything is an object and every operation is message passing".
- `INFECTIONS.md` (Active types) — "Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)" are **explicitly allowed**.

If every `+`, `*`, etc. is a message (`__add__`, `__mul__`), then the "grouping" via Python precedence is an artificial decision — a human reader expects pure message passing.

**Possible implementation:** new transformer at `poop/transformers/binop_left_assoc.py` that rewrites `ast.BinOp` to be left-associative, ignoring precedence:

```python
class _LeftAssocRewriter(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        # Joins BinOp chains in post-order, regrouping left-to-right,
        # except where explicit parentheses already nest the tree.
        ...
```

Detail: explicit parentheses in the source (`3 + (1 * 2)`) become nested subtrees and must be preserved — the transformer only reorders flat chains.

**Trade-offs:**
- **Pro:** consistency with the "everything is a message" principle; POOP code becomes more predictable for someone reading it as a dialogue between objects; aligns with already-adopted Smalltalk-isms (`do:`, `if_true:`).
- **Con:** breaks the expectation of any Python programmer who looks at the code; mathematical expressions need explicit parentheses for the usual semantics (`3 + (1 * 2)`); static tools (ty, IDE inspections) evaluate with Python precedence and could disagree with the runtime; very "infectious" — affects every arithmetic expression in every example.
- **Partial mitigation:** an optional validator that requires parentheses on any chain mixing different operators, forcing the author to be explicit — but that is syntactic noise.

**Cases to consider:**
- Chained comparisons (`a < b < c`) — Python already has special semantics; preserve or reject?
- Unary operators (`-x`) — already banned via `no_unary_minus`, so they do not interfere.
- Augmented assignment (`x += y * z`) — does the RHS undergo the same reordering?

**Effort:** medium (transformer + tests + updates to examples that depend on implicit precedence). **Impact:** observable semantic change in every POOP program with mixed operators; aligns the language with its founding principle.

**Decision:** adopt Smalltalk-style left-to-right evaluation, or keep Python precedence for pragmatism?

---

## Open decisions — import hygiene

### 11. Audit project imports against the `TYPE_CHECKING` rule?

**Rule (`CLAUDE.md:58`):** imports live at module top; function-local `import` only to break a real cycle; imports used **exclusively** in type annotations must live in an `if TYPE_CHECKING:` block at the top of the module — never function-local, never alongside runtime top-level imports.

**Symptoms to look for:**
- `from poop.types.X import Y` function-local where `Y` is used **only in annotations** inside that function (should move to a module-top `if TYPE_CHECKING` block).
- `from poop.types.X import Y` top-level where `Y` is used only in annotations (same fix — move to `TYPE_CHECKING`).
- Function-local imports without an actual cycle (could be hoisted to the top).

**Scope:** sweep `poop/types/*.py`, `poop/transformers/*.py`, `poop/validators/*.py`. For each function-local `import`: confirm whether a cycle exists (try hoisting) and whether the name is used at runtime vs. in annotations only.

**Tooling hint:** `grep -n "    from poop\." poop/**/*.py` lists function-local imports; cross-check with grep for runtime use vs. annotation-only use.

**Effort:** medium (sweep + one commit per affected module). **Impact:** aligns the codebase with the rule; avoids unnecessary lazy-import overhead; clarifies author intent (runtime vs. type-only).

**Decision:** do the audit in one pass, or handle opportunistically when touching each file?

---

## Open decisions — documentation

### 12. Audit and rewrite `INFECTIONS.md` to reflect current state?

**Today:** `INFECTIONS.md` (738 lines) is the canonical catalog of validators, transformers, types, and principles. It was written incrementally since the start of the project, and several sections were added when some decisions were still **open questions** ("maybe", "to be defined", "investigate"). Many of those questions have since been settled in practice (in code, tests, commits), but the document may not have been updated uniformly.

**Drift symptoms motivating the audit:**
- Items still classified as "no POOP equivalent" while a substitute exists in practice (e.g.: `vars`, `setattr`/`delattr` — see proposals 5-7 in this list — a sign that "intentional" turned into inertia).
- Principles phrased as hypotheses ("Methods should follow Python names...") without explicit confirmation that all exceptions are catalogued (`do` is the only exception cited — could others slip through?).
- Validator tables may list AST nodes the current validator does not visit (or vice versa) — drift between code and doc.
- Possible duplicates between `INFECTIONS.md` (principles) and `CLAUDE.md` (workflow) that make it ambiguous which is the source of truth.

**Proposed audit scope:**

1. **Validators** — for each `poop/validators/no_*.py`:
   - confirm the table in `INFECTIONS.md` lists exactly the nodes/calls the validator visits;
   - confirm the promised "Substitute" exists in `poop/types/`;
   - mark validators without a substitute as a "definitive ban" or move them to an explicit backlog.

2. **Transformers** — for each `poop/transformers/*.py`:
   - confirm the documentation covers every node the transformer rewrites;
   - confirm the documented literals ("every literal is transformed") are in fact 100% covered (`int`, `float`, `str`, `bool`, `None`, `list`, `tuple`, `set`, `dict`, `bytes`, `complex` — does each have a transformer? Any gaps?).

3. **Types** — for each `poop/types/*.py`:
   - confirm the page/section for each type lists the current public methods (not those of an earlier version);
   - confirm that dunders → public aliases follow the rule "Dunders exposed as regular methods" with no undocumented exceptions;
   - confirm the rule "All POOP methods return POOP types" by sweeping return values.

4. **Principles** — re-validate each bullet of `## Principles`:
   - Is it descriptive (reflects the code) or aspirational (not yet enforced)?
   - Aspirational → move to `proposals.md` as an explicit item.
   - Descriptive → keep, with a concrete example if it helps.

5. **Historical open questions** — sweep `git log -- INFECTIONS.md` for commits with "wip", "draft", "rascunho", "talvez" or hesitant language; each becomes a question to close (yes/no/proposal).

**Useful tooling:**
- `grep -n "talvez\|a definir\|TODO\|FIXME\|investigar\|? *$" INFECTIONS.md` to flag residual questions.
- Cross-check script: parse validators/transformers/types via AST and compare with `INFECTIONS.md` sections (automated gap analysis).

**Expected output:**
- `INFECTIONS.md` rewritten (or in incremental PRs) where each rule is **descriptive and verified** — mirrors the code.
- Aspirational items migrated to `proposals.md`.
- Live automated cross-reference (script in `scripts/audit_infections.py` run in CI?) — bonus.

**Effort:** large (line-by-line sweep of 738 lines + cross-check against ~60 validators, ~16 transformers, ~17 types). **Impact:** restores `INFECTIONS.md` as a trustworthy SSOT; prerequisite for proposal 13 (MkDocs) — without a consistent doc, generating the site amplifies the drift.

**Decision:** run the audit in a single pass (large effort but settles it for good), or in incremental waves by section (validators first, then transformers, then types)?

### 13. Documentation site with MkDocs?

**Today:** documentation is scattered across `README.md` (overview), `INFECTIONS.md` (validator/transformer/type catalog — 90+ sections), `CLAUDE.md` (internal guide), and `proposals.md` (this backlog). No navigation, no search, no published versioning.

**Proposal:** adopt [MkDocs](https://www.mkdocs.org/) with the [Material](https://squidfunk.github.io/mkdocs-material/) theme to generate a navigable static site.

**Suggested structure under `docs/`:**
- `index.md` — landing page (extracted from `README.md`)
- `getting-started.md` — install, run the first POOP program
- `principles.md` — language principles (extracted from `INFECTIONS.md` "Principles")
- `infections/validators.md` — one entry per validator (generated/extracted from `INFECTIONS.md`)
- `infections/transformers.md` — same for transformers
- `types/` — one page per POOP type (`Object`, `Int`, `Str`, etc.) with their methods
- `examples.md` — pointer to `examples/`
- `contributing.md` — workflow, atomic commits, design principles

**Minimum setup:**
- `mkdocs.yml` at the repo root (config + nav)
- `mkdocs` + `mkdocs-material` in `[dependency-groups.dev]` in `pyproject.toml`
- `uv run mkdocs serve` for local preview; `uv run mkdocs build` to generate `site/`
- Optional: GitHub Pages via Action (`mkdocs gh-deploy`).

**Bonus considerations:**
- `mkdocstrings[python]` to auto-generate API reference from docstrings on POOP types — aligns with the rule "every relevant dunder gets a Python-named alias" and surfaces the rich API.
- `mkdocs-autorefs` plugin for cross-page links.

**Trade-offs:**
- **Keep** `INFECTIONS.md` as the single source of truth and generate pages from it (extraction script) — avoids duplication but requires tooling.
- **Migrate** the content into separate files under `docs/` — cleaner end state, but requires updating the workflow ("After each infection, update `docs/infections/...`" instead of `INFECTIONS.md`).

**Effort:** medium (setup ~1h; content migration depends on the SSOT choice). **Impact:** language discoverability for new users improves dramatically; full-text search on the site; published history.

**Decision:** adopt MkDocs? If yes, which SSOT — `INFECTIONS.md` extracted or `docs/` migrated?

---

## Stay banned (no proposal)

Genuinely without a possible substitute inside POOP's model:

- `exec`/`eval`/`compile` — metaprogramming, contradicts the static principle.
- `exit`/`quit` — process control, outside the object model.
- `breakpoint` — debugger handshake, not a domain operation.
- `globals()`/`locals()` — lexical scope introspection (instance state is already accessible).
- `del` — statement, not a builtin function.
