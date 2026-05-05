# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — substitute exists with a different name

Items where the substitute works, but the method name does not mirror the builtin. Implementing them is optional — depends on whether mirrored names take priority over a leaner API.

### ~~1. `enumerate(col)` → `col.enumerate()` returning a lazy `Enumerate` object?~~ — DONE

**Decision:** lazy `Enumerate(_IterableMixin, Object)` without dependency on proposal 3. `enumerate(col)` and `enumerate(col, start)` are intercepted by `EnumerateTransformer` and rewritten to `_poop_enumerate(...)`. All `_IterableMixin` types and `Dict` expose `.enumerate(start=Int(0)) -> Enumerate`. `Enumerate` inherits `do`, `map`, `filter`, etc. from `_IterableMixin` and works on any iterable including `Dict`.

### ~~2. `zip(a, b)` → `a.zip(other)` returning a lazy `Zip` object?~~ — DONE

**Decision:** lazy `Zip(_IterableMixin, Object)` mirroring Python exactly. `zip(...)` interceptado por `ZipTransformer` → `_poop_zip(...)`. Suporta número variádico de iteráveis e `strict=true` (levanta `ValueError` se tamanhos diferem). Todos os tipos `_IterableMixin` e `Dict` expõem `.zip(*others, strict=false) -> Zip`.

### 3. `iter(col)` / `next(it)` → first-class `Iterator` type?

**Today:** iteration only via `col.do(block)` (`INFECTIONS.md:294`).

**Implementation:** invasive — requires a new `Iterator` type in `poop/types/` plus a matching transformer in `poop/transformers/` (just like `Block` has its own).

**Decision:** introduce a first-class iterator, or keep the pure Smalltalk model (only `do`)?

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### 4. `input(prompt)` → introduce a `Console` / `Stdin` type?

**Today:** `INFECTIONS.md:343-345` declares "interactive I/O — no POOP equivalent".

**Note:** Smalltalk *does* model interactive I/O (`Transcript`, etc.). Natural substitute: a POOP `Console` object with `Console.read_line(prompt: Str) -> Str`.

**Scope:** large — a brand new I/O subsystem.

**Decision:** worth the investment, or keep banned?

### 5. `open(path)` → POOP `Path` type inspired by `pathlib`?

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

### 6. Smalltalk-style binary operator evaluation (left-to-right, no precedence)?

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

## Open decisions — API review

### ~~7. Audit methods returning `self` — should they mirror Python instead?~~ — DONE (option c)

**Decision:** hybrid (c) — mutators named after Python void-returning methods (`append`, `clear`, `extend`, `insert`, `remove`, `reverse`, `sort`, `update`, `discard`, `intersection_update`, `difference_update`, `symmetric_difference_update`) now return POOP `none`. POOP-specific methods (`List.add`, `Dict.at_put`, `ByteArray.at_put`) that have no Python equivalent keep returning `self`. Identity methods (`Int.real`, `NoneClass.if_not_none`, `Try.run`, `With.do`) are unchanged. Principle added to `INFECTIONS.md`.

### 8. Audit `__slots__` usage on POOP types?

**Today:** `INFECTIONS.md` declares the principle: *"`__slots__` on all POOP types: instance variables are declared in the class definition and fixed — never added dynamically to instances. Subclasses that need new instance variables can declare their own `__slots__` or omit them."*

A quick survey of `poop/types/*.py` shows every type currently declares `__slots__`:

| Pattern | Types |
|---|---|
| `__slots__ = ()` | `Object`, `Boolean` (and the abstract `_TrueClass`/`_FalseClass`), `NoneClass` |
| `__slots__ = ("_value",)` | `Int`, `Float`, `Complex`, `Str`, `Bytes`, `ByteArray`, `MemoryView` |
| `__slots__ = ("_items",)` | `List`, `Tuple` |
| `__slots__ = ("_data",)` | `Set`, `FrozenSet`, `Dict` |
| `__slots__ = ("_start", "_step", "_stop")` | `Range` |
| `__slots__ = ("_block", "_finally_block", "_handlers")` | `Try` |
| `__slots__ = ("_cm_block",)` | `With` |
| `__slots__ = ("_fn",)` | `Block` |
| `__slots__ = ("_exception",)` | `Error` |

So the principle is currently **descriptively accurate** for the library types. The audit asks the deeper questions:

**Open sub-questions:**

1. **Naming consistency.** Three different conventions coexist for "the wrapped Python value":
   - `_value` for scalar wrappers (`Int`, `Float`, `Str`, …) — including `MemoryView` and `ByteArray` which wrap mutable structures.
   - `_items` for sequence wrappers (`List`, `Tuple`).
   - `_data` for set/dict wrappers (`Set`, `FrozenSet`, `Dict`).
   Should these collapse to a single `_value` everywhere (uniform), stay split by category (current — descriptive), or be renamed to follow Python's semi-standard `__wrapped__` / `_inner`?

2. **End-user classes.** The principle is written about library types; there is no enforcement (validator) that user classes inheriting from `Object` must declare `__slots__`. Should there be? Today a user can write `class Foo(Object): pass` and freely set arbitrary attributes — directly contradicting the spirit of the rule.

3. **Empty `__slots__ = ()`.** `Object`, `Boolean`, `NoneClass` declare empty slots. This is functionally the same as inheriting from a slotted base, but makes the declaration explicit. Is the explicit empty-tuple a documented requirement, or an accident? Could it be skipped on abstract types (`Boolean`)?

4. **Annotation alignment.** Several types declare slot names as strings in `__slots__` and again in `__init__` — but no class-level type annotation matches the slot. This means `ty` cannot infer the slot's type from the class definition (only from the `__init__` body). Should slots be paired with class-level annotations (e.g., `__slots__ = ("_value",)` plus `_value: int`) for static-typing clarity?

5. **`__hash__ = None` + slots.** `List`, `ByteArray`, `Set`, `Dict` declare `__hash__ = None` to be explicitly unhashable. This is a class attribute, not a slot — and Python's slot machinery requires care so that `__hash__ = None` does not collide with slot generation. Should this pattern be lifted into a base class or mixin?

**Effort:** (1) medium — rename + tests/examples touched. (2) medium — new validator + tests. (3) small — documentation. (4) medium — sweep types adding annotations. (5) small — mixin extraction.

**Impact:** principle hygiene; sets the stage for tighter static guarantees; closes the gap between "library types follow `__slots__`" and "user classes inheriting from `Object` may not".

**Decision:** which sub-questions to act on, and in what order? Or accept the current state as descriptively correct and leave only documentation tightening?

### 11. Audit POOP-only methods — document them and verify they behave like their Python equivalents

**Today:** POOP defines a number of methods that have no Python method counterpart — they exist because POOP bans syntax constructs (`[]`, `in`, `len()`, etc.) and replaces them with object messages. These are not named after a Python method; they are a new API invented by POOP:

| POOP method | Replaces | Python semantics |
|---|---|---|
| `obj.at(idx)` | `obj[idx]` | `__getitem__` |
| `obj.at_put(idx, val)` | `obj[idx] = val` | `__setitem__` |
| `obj.includes(x)` | `x in obj` | `__contains__` |
| `obj.len()` | `len(obj)` | `__len__` |
| `List.add(x)` | `list.append(x)` but returns `self` | no Python method equivalent |
| `List.first()` / `List.last()` | `lst[0]` / `lst[-1]` | `__getitem__` |
| `obj.do(block)` | `for x in obj: block(x)` | iteration |
| `obj.map(fn)` | `[fn(x) for x in obj]` / `map(fn, obj)` | — |
| `obj.filter(fn)` | `[x for x in obj if fn(x)]` / `filter(fn, obj)` | — |
| `obj.filter_false(fn)` | `[x for x in obj if not fn(x)]` / `filterfalse(fn, obj)` | — |
| `obj.find(fn)` | `next((x for x in obj if fn(x)), None)` | — |
| `obj.sum()` | `sum(obj)` | — |
| `obj.all(fn)` | `all(fn(x) for x in obj)` | — |
| `obj.any(fn)` | `any(fn(x) for x in obj)` | — |

**Two sub-concerns:**

1. **Syntax-substituting methods** (`at`, `at_put`, `includes`, `len`) — these ARE semantically Python, just expressed as messages instead of syntax or builtins. Their contract should be identical to Python (`at(idx)` raises `IndexError` for out-of-range, `at_put` on an immutable type raises `TypeError`, etc.). Currently there is no explicit documentation that each of these mirrors Python exactly, and no tests that verify the error cases.

2. **New POOP-specific methods** (`add`, `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any`, `first`, `last`) — these are convenient abstractions, some from Smalltalk (`do`), some from Python's functional API (`map`, `filter`). Their semantics and return types are not documented anywhere beyond reading the implementation.

**What is missing:**
- An `INFECTIONS.md` section (or supplementary document) cataloguing each POOP-only method with: what it replaces, its contract, its return type, and any edge cases.
- Tests covering edge-case parity with Python for syntax-substituting methods (e.g., `at` with negative index, `at` out of bounds, `at_put` on immutable types).
- Confirmation that `at` on `Dict` returns `none` for missing keys (POOP semantics differ from `KeyError` — this is intentional but undocumented).

**Options:**

- **(a) Catalogue only.** Add a section to `INFECTIONS.md` listing all POOP-only methods grouped by category (syntax substitutes, iteration, functional). No behavior changes.
- **(b) Catalogue + edge-case tests.** Same as (a), plus add tests for out-of-bounds, immutable `at_put`, and other boundary conditions that should match Python.
- **(c) Strict parity for syntax-substituting methods.** Change `Dict.at` to raise `KeyError` on missing key (matching Python `dict[key]`), and add a separate `get(key)` returning `none`. Maximizes Python-mirror fidelity.

**Effort:** (a) small. (b) medium. (c) medium + breaking change.

**Decision:** catalogue only (a), catalogue + tests (b), or enforce strict parity (c)?

---

## Open decisions — documentation

### 9. Audit and rewrite `INFECTIONS.md` to reflect current state?

**Today:** `INFECTIONS.md` is the canonical catalog of validators, transformers, types, and principles. It was written incrementally since the start of the project, and several sections were added when some decisions were still **open questions** ("maybe", "to be defined", "investigate"). Many of those questions have since been settled in practice (in code, tests, commits), but the document may not have been updated uniformly.

**Drift symptoms motivating the audit:**
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

**Effort:** large (line-by-line sweep + cross-check against ~60 validators, ~16 transformers, ~17 types). **Impact:** restores `INFECTIONS.md` as a trustworthy SSOT; prerequisite for proposal 10 (MkDocs) — without a consistent doc, generating the site amplifies the drift.

**Decision:** run the audit in a single pass (large effort but settles it for good), or in incremental waves by section (validators first, then transformers, then types)?

### 10. Documentation site with MkDocs?

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
- `vars(obj)` — exposes Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects; breaks encapsulation and the "all methods return POOP types" rule.
- `del` — statement, not a builtin function.
