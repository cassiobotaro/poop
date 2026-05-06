# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### 1. `open(path)` → POOP `Path` type inspired by `pathlib`?

**Today:** `INFECTIONS.md` declares "file I/O — no POOP equivalent".

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

### 2. Smalltalk-style binary operator evaluation (left-to-right, no precedence)?

**Today:** Python evaluates `3 + 1 * 2` as `3 + (1 * 2) = 5` (precedence: `*` before `+`). POOP inherits that because the parser is Python's (`poop/parser.py` → `ast.parse`).

**In Smalltalk:** binary messages are evaluated **left-to-right with no precedence**. `3 + 1 * 2` reads as "send `+ 1` to `3`, then `* 2` to the result" → `(3 + 1) * 2 = 8`. It is a direct consequence of the principle "everything is a message to an object".

**Tension between POOP principles:**
- `INFECTIONS.md:8` — "Everything is an object and every operation is message passing".
- `INFECTIONS.md` (Active types) — "Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)" are **explicitly allowed**.

If every `+`, `*`, etc. is a message (`__add__`, `__mul__`), then the "grouping" via Python precedence is an artificial decision — a human reader expects pure message passing.

**Possible implementation:** new transformer at `poop/transformers/binop_left_assoc.py` that rewrites `ast.BinOp` to be left-associative, ignoring precedence.

Detail: explicit parentheses in the source (`3 + (1 * 2)`) become nested subtrees and must be preserved — the transformer only reorders flat chains.

**Trade-offs:**
- **Pro:** consistency with the "everything is a message" principle; POOP code becomes more predictable for someone reading it as a dialogue between objects; aligns with already-adopted Smalltalk-isms (`do:`, `if_true:`).
- **Con:** breaks the expectation of any Python programmer who looks at the code; mathematical expressions need explicit parentheses for the usual semantics (`3 + (1 * 2)`); static tools (ty, IDE inspections) evaluate with Python precedence and could disagree with the runtime; very "infectious" — affects every arithmetic expression in every example.

**Cases to consider:**
- Chained comparisons (`a < b < c`) — Python already has special semantics; preserve or reject?
- Unary operators (`-x`) — already banned via `no_unary_minus`, so they do not interfere.
- Augmented assignment (`x += y * z`) — does the RHS undergo the same reordering?

**Effort:** medium (transformer + tests + updates to examples that depend on implicit precedence). **Impact:** observable semantic change in every POOP program with mixed operators; aligns the language with its founding principle.

**Decision:** adopt Smalltalk-style left-to-right evaluation, or keep Python precedence for pragmatism?

---

## Open decisions — API review

### 3. Audit `__slots__` usage on POOP types?

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

### 4. Conversion method naming — `Str.int()`, `Int.float()`, etc.?

**Context:** Type constructor calls (`int(expr)`, `float(expr)`, `str(expr)`, etc.) are already intercepted by the existing transformers — `int(Str("42"))` correctly produces a POOP `Int` at runtime. This is documented in `INFECTIONS.md` as "Constructor builtins are intercepted, not banned".

**Remaining question:** POOP types also expose conversion as methods: `Str("42").int() -> Int`, `Str("3.14").float() -> Float`, `Int(3).float() -> Float`, etc. (e.g., `poop/types/string.py:39`, `poop/types/int.py:86`).

The method name `int` on `Str` is the same identifier as the Python type `int`. A human reading `Str("42").int()` may be momentarily confused about whether `int` is a method or a constructor call. This is purely a readability concern — the execution is unambiguous.

**Options:**

- **(a) Status quo** — keep `Str.int()`, `Int.float()`, etc. The method names follow the Python convention ("Python names, not Smalltalk names"). The transformer already intercepts the bare `int(expr)` call form, so both forms work correctly. The naming is consistent with how `ord()` on `Str` mirrors `ord(c)` the builtin.
- **(b) Rename to `to_int()`, `to_float()`** — eliminates the ambiguity at the cost of breaking the "Python names" principle. `Str("42").to_int()` reads as an explicit conversion, not a constructor lookup.

**Decision:** keep status quo (a) or rename (b)?

### 5. `Dict.keys()` / `values()` / `items()` → live view objects?

**Today:** `Dict.keys()`, `Dict.values()`, `Dict.items()` (`poop/types/dict.py`) eagerly build and return a `List`. Snapshots — they do not reflect later mutations of the dict.

**In Python:** these methods return live view objects (`dict_keys`, `dict_values`, `dict_items`) that:
- reflect dict mutations after the view was created;
- are iterable (each yields its corresponding `dict_*iterator`);
- expose `len()` / `__contains__`;
- `dict_keys` and `dict_items` (when values are hashable) support **set operations** (`|`, `&`, `-`, `^`).

**Proposed direction:** introduce three POOP types — `DictKeys`, `DictValues`, `DictItems` — wrapping the native Python view (`__slots__ = ("_view",)`), inheriting `_IterableMixin` so `do`/`map`/`filter`/etc. work, and exposing `len()`, `includes(x)`, `__iter__` lazy.

For `DictKeys` and `DictItems`: also implement set ops (`union`, `intersection`, `difference`, `symmetric_difference`, plus `|`, `&`, `-`, `^` infix) returning POOP `Set`. Mirrors Python's view algebra.

**Open questions:**

- **(a) Liveness vs eagerness.** The current snapshot semantics may be a deliberate simplification. Live views are more powerful but also more surprising — a long-held view sees later mutations. Adopt liveness (Python parity) or keep snapshot (current)?
- **(b) Set ops on `DictValues`?** Python rejects them because values may be unhashable. Match Python (no set ops on values) or relax (allow when all values are hashable)?
- **(c) Migration impact.** Several call sites in `examples/` and `tests/` rely on `keys()`/`values()`/`items()` returning a `List` (e.g., `.at(Int(0))`, `.append(...)`). Switching to a view breaks those — but the view does have `_IterableMixin`, so `.do(block)` etc. continue to work. How aggressive: full break (Python parity), or keep `.list()` / `.to_list()` escape hatch on the view?

**Suggested files:**
- `poop/types/dict_keys.py` (new)
- `poop/types/dict_values.py` (new)
- `poop/types/dict_items.py` (new)

**Effort:** medium — three new types + update `Dict.keys/values/items` + sweep callers.

**Decision:** adopt live views (a)? Set ops on values (b)? Hard break or escape hatch (c)?

### 6. `DictValueIterator` and `DictItemIterator`?

**Today:** Only `DictKeyIterator` exists (returned by `Dict.iter()`, mirroring Python's `iter(dict)`). Value and item iterators were explicitly deferred when the iterator subsystem landed.

**In Python:**
- `iter(d.values())` returns a `dict_valueiterator`
- `iter(d.items())` returns a `dict_itemiterator`

These are distinct types from `dict_keyiterator` even though their `__next__` is structurally identical to `_IteratorBase`.

**Proposed direction:** add `DictValueIterator` and `DictItemIterator` as `_IteratorBase` subclasses. They are returned by `.iter()` on the corresponding view objects from proposal #5.

```python
class DictValues:
    def iter(self) -> DictValueIterator:
        return DictValueIterator(self._view)

class DictItems:
    def iter(self) -> DictItemIterator:
        return DictItemIterator(self._view)
```

Each iterator's `next()` yields the right shape — for `DictItemIterator`, each `next()` returns a `Tuple(key, value)` (matching Python).

**Dependency:** this proposal **requires #5** — without view objects, there is nowhere natural to hang `.iter()` for values/items.

**Open question:** if proposal #5 is rejected (snapshot kept), does this proposal still make sense? Possible fallbacks:
- **(a) Drop it** — without views, there is no "thing" whose iterator type would be returned; `Dict.values()` returns a `List`, and `List.iter()` already returns `ListIterator`.
- **(b) Add `Dict.iter_values()` / `Dict.iter_items()` methods directly on Dict** — bypasses the view layer entirely; less faithful to Python but unblocks the iterator types.

**Suggested files:**
- `poop/types/dict_value_iterator.py` (new)
- `poop/types/dict_item_iterator.py` (new)

**Effort:** small (after #6 is in) — two thin iterator subclasses + the `.iter()` methods on the views.

**Decision:** depends on #5 outcome. If #5 adopted, this is straightforward; if rejected, choose (a) drop or (b) Dict.iter_values()/iter_items().

---

## Open decisions — documentation

### 7. Audit and rewrite `INFECTIONS.md` to reflect current state?

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

**Effort:** large (line-by-line sweep + cross-check against ~60 validators, ~16 transformers, ~17 types). **Impact:** restores `INFECTIONS.md` as a trustworthy SSOT; prerequisite for proposal 8 (MkDocs) — without a consistent doc, generating the site amplifies the drift.

**Decision:** run the audit in a single pass (large effort but settles it for good), or in incremental waves by section (validators first, then transformers, then types)?

### 8. Documentation site with MkDocs?

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

### 9. Add a `CONTRIBUTING.md`?

**Today:** there is no `CONTRIBUTING.md` at the repo root. Contributor guidance is split between `CLAUDE.md` (workflow + conventions, but framed for an AI agent) and `INFECTIONS.md` (language principles, written as a catalog). A first-time human contributor has no canonical entry point — they must read `CLAUDE.md` and infer which parts apply.

**Drift symptoms motivating this:**
- Atomic-commit rule lives in `CLAUDE.md:42` but should be enforced for any contributor.
- The convention "every example needs a Smalltalk version" lives only in commit history — not documented anywhere; was discovered when `slicing.py` slipped through.
- Imports-at-top, English-in-`proposals.md`, and "verify GitHub Action versions are current" rules are buried in `CLAUDE.md` Conventions.
- Pre-commit setup (`prek` + `.pre-commit-config.yaml`) is mentioned in passing in `CLAUDE.md:38` but not in any onboarding doc.

**Proposed scope for `CONTRIBUTING.md`:**

1. **Getting started** — `uv sync --dev`, running `poop file.py`, running tests.
2. **Workflow**
   - Atomic commits: one validator, one type, one bug fix per commit.
   - Confirm scope before multi-part plans.
   - Pre-commit hooks (`prek install`).
3. **Conventions**
   - Imports at top of module; `if TYPE_CHECKING` block for type-only.
   - `proposals.md` written in English regardless of conversation language.
   - Every example in `examples/` must have a corresponding Smalltalk version in its docstring.
   - Use the actual current year in dates / copyright / license.
4. **Adding a new validator / transformer / type** — checklist:
   - File location (`poop/validators/`, `poop/transformers/`, `poop/types/`).
   - Register in `DEFAULT_VALIDATORS` / `DEFAULT_TRANSFORMERS` / namespace.
   - Add tests under `tests/`.
   - Update `INFECTIONS.md` with the catalog entry.
5. **Closing a proposal** — pattern observed in commits:
   - Implement in atomic commits.
   - Strike the heading (`### ~~N. ...~~ — DONE`) **or** remove + renumber + update cross-references.
   - Update `INFECTIONS.md` if the proposal affects validators/types.
6. **Pull requests** — branch naming, description format, what to test before opening.

**Open questions:**

- **(a) Location.** `CONTRIBUTING.md` at root (GitHub auto-links it from the "New PR" page) vs. `docs/contributing.md` (consumed by MkDocs proposal 8). A common pattern is one at root with a stub that links to the MkDocs page; or symlink.
- **(b) Source distribution.** Distill from `CLAUDE.md` (some sections are AI-specific — *"Defer to user judgement"*, etc., do not belong in `CONTRIBUTING.md`) or write fresh.
- **(c) Relationship to `CLAUDE.md`.** Once `CONTRIBUTING.md` exists, `CLAUDE.md` should reference it ("conventions documented in `CONTRIBUTING.md`") to avoid drift between the two.
- **(d) Code of conduct.** Bundle a Contributor Covenant section into `CONTRIBUTING.md`, add a separate `CODE_OF_CONDUCT.md`, or skip for now (small project, single maintainer)?

**Effort:** small (~2h to draft + review). **Impact:** lowers barrier for human contributors; codifies conventions discovered ad-hoc (Smalltalk-in-examples, atomic commits).

**Decision:** adopt? If yes, settle (a) location and (d) code of conduct.

---

## Stay banned (no proposal)

Genuinely without a possible substitute inside POOP's model:

- `exec`/`eval`/`compile` — metaprogramming, contradicts the static principle.
- `exit`/`quit` — process control, outside the object model.
- `breakpoint` — debugger handshake, not a domain operation.
- `globals()`/`locals()` — lexical scope introspection (instance state is already accessible).
- `vars(obj)` — exposes Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects; breaks encapsulation and the "all methods return POOP types" rule.
- `del` — statement, not a builtin function.
