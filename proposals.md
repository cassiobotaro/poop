# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **consistency**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Bugs

Found while writing the `docs/python-vs-poop/` pages — every snippet
was executed against the real interpreter, and these are the bugs
that didn't run cleanly. The docs document the **intended** idiomatic
call (matching each method's declared signature); these proposals are
about closing the gap between the signature and the implementation.

### 1. Public POOP type names not exposed in the user namespace

**Today:** `DEFAULT_NAMESPACE`
(`poop/transformers/__init__.py:56-80`) is built from
`*Transformer.BINDINGS` dicts, and each transformer (e.g.
`StrTransformer.BINDINGS` at `poop/transformers/string.py:45-48`,
`IntTransformer.BINDINGS` at `poop/transformers/int.py:73-76`) exposes
only the `_poop_*` private names — not `Str`, `Int`, `List`, `Dict`,
etc. As a result `x.is_instance(Str)` raises
`name 'Str' is not defined`, which makes the
`Object.is_instance(type_)` API unusable for POOP's own types from
user code.

**Repro:**
```python
"hi".is_instance(Str).print()
# poop: name 'Str' is not defined
```

**Possible models:**
- **(a) Add public bindings.** Each transformer exposes both `_poop_str`
  and `Str` (etc.). `is_instance` then works against any POOP type
  the user can name. Risk: user code can shadow `Str` and confuse
  literals; mitigated because `_poop_str` is the literal-construction
  path, not `Str`.
- **(b) Provide a `types` namespace.** Inject a `types` (or `poop`)
  module-like object exposing `types.Str`, `types.Int`, etc. Avoids
  shadowing risk; costs an extra hop.
- **(c) Resolve names lazily inside `is_instance`.** Accept a string
  literal — `x.is_instance("Str")` — and look it up in a registry.
  Bigger semantic change; loses static typing discipline.

**Recommendation:** (a). The current state already breaks the documented
API; adding the bindings is the smallest change and the closest match
to how a Python user would expect `isinstance` replacements to feel.

**Workaround for users today:** `is_instance` works only against
user-defined classes (`x.is_instance(MyClass)`), since user names live
in their own scope.

---

## Consistency

### 1. Tighten public method signatures to POOP-only types

**Today:** several public methods on POOP types declare parameters as
Python primitives (`int`, `str`, `bool`) instead of the corresponding
POOP types. At runtime in POOP source the transformer wraps every
literal — `1` → `Int(1)`, `"foo"` → `Str("foo")`, `True` → POOP
`Boolean` — so any user call passes POOP types. The signatures are
"leaky": they suggest two callers (Python and POOP) when only POOP
exists in the executed pipeline. The only consumer that still passes
Python primitives is the unit-test suite, which runs methods directly
without the transformer.

This came up while fixing the `round(ndigits)` and `*_attr(name)`
bugs in commits `9f66513` and `c3c36e1`: both fixes accepted
`Int | int` / `Str | str` instead of tightening to `Int` / `Str`
only. The looser signature avoids touching test code but contradicts
the established convention — `Int.to_bytes(length: Int, byteorder:
Str)`, `Float.divmod(other: Float)`, and `Object.format(spec: Str |
None)` already accept POOP-only.

**Concrete leak still present (becomes a runtime bug from POOP):**

`Object.print(end: str = "\n", flush: bool = False)`
(`poop/types/object.py:112`) — and the overrides on `List`
(`poop/types/list.py:147`) and `Tuple` (`poop/types/tuple.py:113`)
which add `sep: str = " "`. Repro:

```python
"hello".print(end=" ")
# poop: end must be None or a string, not Str
```

**Fix sketch:**
1. Tighten the just-fixed methods (`Float.__round__`, `Int.__round__`,
   `Object.has_attr`, `Object.get_attr`, `Object.set_attr`,
   `Object.del_attr`) to accept POOP types only; update unit tests
   to construct POOP types at the call site.
2. Fix `Object.print` / `List.print` / `Tuple.print` the same way:
   `end: Str = Str("\n")`, `sep: Str = Str(" ")`, `flush: Boolean =
   false` — unwrap via `_value` (or `bool(...)`) before delegating to
   the Python `print` builtin.
3. Audit the rest of `poop/types/` for the same shape. Initial
   candidates to inspect: any public method with a `: int` / `: str` /
   `: bool` annotation that does not look like a constructor or a
   dunder Python invokes directly (`__init__`, `__str__`, `__hash__`,
   `__bool__`, etc.). `grep -rn "def [a-z_]*.*: \(str\|int\|bool\)" poop/types/`
   is a reasonable starting filter.

**Out of scope (intentionally Python-typed):**
- Constructors (`Int.__init__(self, value: int)`): they are the
  bridge from Python land into POOP and are called by the transformer
  itself.
- Dunders that Python's runtime invokes and whose return type the
  language pins (`__str__ -> str`, `__hash__ -> int`, `__bool__ ->
  bool`, `__int__ -> int`).
- Truly private helpers prefixed with `_`.

**Recommendation:** approve as a single audit-and-tighten PR, or
split into one PR per type (Object, List, Tuple, …). Either way the
guideline going forward is: a POOP method's public signature uses
POOP types; primitives appear only at the boundaries.

**Decision:** approve the audit and the convention?

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
- ~~**Python ↔ POOP comparison table.**~~ **DONE** — shipped as the
  `docs/python-vs-poop/` section: an overview plus three didactic
  pages (`conditionals.md`, `loops.md`, `builtins.md`) using a fixed
  Python → POOP → Why → See also template. Every page assumes Python
  knowledge and treats Smalltalk as a curiosity aside. Cross-linked
  from `docs/index.md` and `docs/getting-started.md`.
- ~~**REPL guide.**~~ **DONE** — `docs/repl.md` documents the REPL
  (`poop` with no arguments): banner, prompts, pre-loaded namespace,
  multi-line input, tab completion, history, `_` shortcut, and the
  `poop: <message>` error format. Surfaced in the site nav and linked
  from `docs/index.md` and `docs/getting-started.md`.
- ~~**Guided tutorial.**~~ **DONE** — `docs/tutorial/` with an
  overview and six lessons (Strings, Conditionals, Iteration,
  Classes, Collections, Errors). Every lesson follows the
  Goal → What's new → Walk-through → Try it → Anchor example →
  Reference template, anchored on a real file in `examples/`. Each
  POOP snippet was executed against the interpreter before publish.
  Closes with a pointer to `examples/rpn_calculator.py` as a
  capstone.
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
"Principles" + types pages → ~~(2) Python ↔ POOP comparison table~~
**(2 done)** → ~~(2.5) REPL guide + Tutorial~~ **(also done)** →
(3) "Why POOP?" + cookbook → (4) the rest. The cookbook can now link
to the `docs/python-vs-poop/` pages and the tutorial lessons instead
of restating the substitutions.

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
