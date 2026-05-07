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

## Open decisions — documentation

### 2. Build out the docs site with comparison tables and learning content

**Today:** the MkDocs site (proposal closed in commit `97923d3` and
follow-ups) has only three thin landing pages: `index.md`,
`getting-started.md`, `contributing.md`. The substantive technical
content still lives in `INFECTIONS.md` (90+ entries) and in
inline-only form in `README.md`. There is no learning-oriented
material — no full Python ↔ POOP comparison, no design rationale, no
cookbook, no glossary.

**Proposal:** treat the docs site as a real product and ship two
complementary tracks:

1. **Migration track** — move existing technical content out of the
   monolithic Markdown files into per-topic pages so the site can be
   navigated and searched.
2. **Enrichment track** — write new content that the project does not
   have anywhere yet, focused on teaching POOP to Python users (the
   most likely audience) and Smalltalk users (the inspiration).

**Migration scope:**
- `docs/principles.md` — extracted from `INFECTIONS.md` "Principles".
- `docs/infections/validators.md` and `docs/infections/transformers.md` — extracted from `INFECTIONS.md` "Active infections".
- `docs/types/` — one page per POOP type, with method tables and examples.
- `docs/examples.md` — categorized index of `examples/` with short explanations.
- Move `CONTRIBUTING.md` body into `docs/contributing.md`; update the workflow rule "Add an entry to `INFECTIONS.md`" to point at the new structure.
- Once migration completes: delete `INFECTIONS.md`; add `mkdocstrings[python]` for auto-API and `mkdocs-autorefs` for cross-page links.

**Enrichment scope (new content, in priority order):**
- **Python ↔ POOP comparison table.** Today the README has a 10-row "Key substitutions" snippet. Expand to a full reference covering control flow (`if`/`for`/`while`/`try`), collections (literals + indexing + slicing + comprehensions), iteration (`map`/`filter`/`reduce`/`sum`), error handling (`raise`/`try`/`except`), comparison/identity (`==`/`is`/`in`), boolean operators (`and`/`or`/`not`), arithmetic (unary `-`/`+`/`~`), introspection (`len`/`abs`/`hash`/`isinstance`), I/O (`print`/`input`/`open`). Side-by-side, runnable, with the POOP version showing the message-passing model.
- **"Why POOP?"** — short essay on the philosophy: every operation as a message, no procedural escape hatches, why we chose Python method names over Smalltalk's, what the project is *not* (production tool, performance-oriented).
- **Cookbook / patterns.** Common idioms with explanation: FizzBuzz, leap year, recursion-instead-of-loop, blocks vs lambdas, conditional dispatch via `if_true_if_false`, `do:` vs `map:`, composing transformers. Each entry: problem statement → naive Python → POOP version → commentary on what changed and why.
- **Smalltalk ↔ POOP bridge.** For readers familiar with Smalltalk: which messages map directly (`do:` → `do`), which renamed (`collect:` → `map`, `select:` → `filter`, `inject:into:` → `reduce`), and what is intentionally absent (cascades, keyword messages).
- **Pipeline walkthrough.** Diagram + prose for `parse → validate → transform → execute(namespace)`. Show the same source through each stage (raw AST, after validators reject, after transformers rewrite, final namespace) — makes the architecture concrete for contributors.
- **Common pitfalls.** Type annotations being misleading (`x: int` holds an `Int` at runtime), naked Python primitives leaking from extension code, `__bool__`/`__hash__` having to return native types, etc. The README has a paragraph on type annotations; expand into a dedicated page.
- **Glossary.** Define "validator", "transformer", "infection", "POOP type", "block", "namespace", "active vs definitive ban".
- **Cheat sheet.** One-page printable quick-reference with the 30–40 most common conversions.

**Deferred / nice-to-have:**
- API reference auto-generated via `mkdocstrings[python]` from POOP type docstrings (depends on the per-type pages existing first).
- Searchable validator/transformer index with filter chips.
- Versioned docs (`mike` plugin) once a 1.0 release is on the horizon.

**Recommendation:** sequence the work as (1) migration of `INFECTIONS.md`
"Principles" + types pages → (2) Python ↔ POOP comparison table → (3)
"Why POOP?" + cookbook → (4) the rest. The comparison table delivers
the highest visible-value-per-hour for new readers and unblocks
linking from cookbook entries.

**Scope:** large, multi-PR. Each enrichment item is one atomic PR per
the project's atomic-commit rule — they are independent and can be
tackled out of order if a contributor has a preference.

**Decision:** approve the two-track plan and the recommended
sequence? Drop or add items? Choose a different first deliverable?

---

## Stay banned (no proposal)

Genuinely without a possible substitute inside POOP's model:

- `exec`/`eval`/`compile` — metaprogramming, contradicts the static principle.
- `exit`/`quit` — process control, outside the object model.
- `breakpoint` — debugger handshake, not a domain operation.
- `globals()`/`locals()` — lexical scope introspection (instance state is already accessible).
- `vars(obj)` — exposes Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects; breaks encapsulation and the "all methods return POOP types" rule.
- `del` — statement, not a builtin function.
