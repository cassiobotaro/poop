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

---

## Open decisions — documentation

### 5. Documentation site with MkDocs?

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

### 6. Document missing types in `INFECTIONS.md`

**Today:** the `## Active types` section in `INFECTIONS.md` only catalogues an API for `Object`, `NoneClass`, `Boolean`, `Block`, `Range`, `Error`, `Try`, `With`, the `_IterableMixin` shared methods, `Object.print`, the three `Dict views`, and `MappingProxy`. The remaining types appear only under `## Active transformers` (which describes AST rewrites, not the type's API) or as scattered notes.

**Types currently without a dedicated API section:**

- Scalars: `Int`, `Float`, `Complex`
- Sequences: `Str`, `Bytes`, `ByteArray`, `MemoryView`
- Collections: `List`, `Tuple`, `Set`, `FrozenSet`, `Dict`
- Lazy iterables: `Enumerate`, `Zip`
- Slicing: `Slice` (has a section under `## Slicing` at the end of the file, structurally inconsistent with the others)
- Iterators: `_IteratorBase`, `ListIterator`, `TupleIterator`, `SetIterator`, `FrozenSetIterator`, `DictKeyIterator`, `DictValueIterator`, `DictItemIterator`, `DictReverseKeyIterator`, `DictReverseValueIterator`, `DictReverseItemIterator`, `StrIterator`, `RangeIterator`, `BytesIterator`, `ByteArrayIterator`, `MemoryViewIterator`

That is **~28 types** without canonical API documentation in `INFECTIONS.md`.

**Discovery context:** flagged during the closed `INFECTIONS.md` audit (Wave 3a). The audit could only verify drift on already-documented types; missing sections fell out of scope.

**Proposed scope:**

1. **One section per type** under `## Active types`, with a method table (Smalltalk message → POOP method → behavior, where applicable; otherwise just method/behavior).
2. **Move `Slice`** from `## Slicing` (end of file) into `## Active types` for consistency.
3. **Iterator section**: a single block explaining `_IteratorBase` and listing the 11 specialized iterators in a table — they share an API and are mostly interchangeable.
4. **Cover all dunders → public alias mappings** explicitly. The principle "Dunders exposed as regular methods" needs every exception called out.
5. **Sweep return-types** to confirm the rule "All POOP methods return POOP types" is descriptive (not aspirational).

**Effort:** medium-large. Each scalar/collection has 20–60 public methods; iterators are smaller. Splitting by type category lets the work proceed in waves (e.g. one commit per type or per category).

**Open questions:**

- **(a) Granularity.** One commit per type (~28 commits), or per category (~5: scalars, sequences, collections, iterables, iterators)?
- **(b) Source-of-truth interaction.** If proposal `#5` (MkDocs) is adopted with `docs/` as SSoT, is this work better done directly under `docs/types/*.md` instead? Trade-off: deciding `#5` first avoids redoing the work; doing this first gives `#5` something to render.
- **(c) Curated vs exhaustive.** The `Object` section is curated (mapped to Smalltalk messages, with a "see source for full list" note added in this audit). Should other type sections follow the same pattern, or be exhaustive?

**Decision:** adopt? If yes, settle (a) granularity and (c) curated-vs-exhaustive.

---

## Stay banned (no proposal)

Genuinely without a possible substitute inside POOP's model:

- `exec`/`eval`/`compile` — metaprogramming, contradicts the static principle.
- `exit`/`quit` — process control, outside the object model.
- `breakpoint` — debugger handshake, not a domain operation.
- `globals()`/`locals()` — lexical scope introspection (instance state is already accessible).
- `vars(obj)` — exposes Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects; breaks encapsulation and the "all methods return POOP types" rule.
- `del` — statement, not a builtin function.
