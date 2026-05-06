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

### 2. Documentation site with MkDocs?

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
