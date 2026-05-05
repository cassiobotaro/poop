# Improvement Proposals

Prioritized list of improvements verified against the code, with real `file:line` references. Categories: **bug**, **open decision**.

Guiding principle (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Open decisions — substitute exists with a different name

Items where the substitute works, but the method name does not mirror the builtin. Implementing them is optional — depends on whether mirrored names take priority over a leaner API.

### 1. `enumerate(col)` → `col.enumerate()` returning a lazy `Enumerate` object?

**Suggested location:** `poop/types/enumerate.py` (new) plus a hook on `poop/types/_iterable_mixin.py` so every collection (`List`, `Tuple`, `Set`, `Range`, `Bytes`, `ByteArray`) inherits `.enumerate()`.

**Today:** `INFECTIONS.md:287` points to `col.map(block)` / `col.reduce(init, block)` with manual indexing.

**Two possible shapes:**

- **(a) Eager `List` of `Tuple(Int(index), item)`.** Cheap (~5 lines on `_IterableMixin`), matches every other collection method (`map`, `filter`, `reduce` are all eager). Materializes the whole list upfront — wasteful on large inputs.
- **(b) Lazy `Enumerate(Object)` object — preferred.** Mirrors Python's `enumerate` semantics 1:1: an iterator that yields `Tuple(Int(index), item)` on demand. Memory-efficient, single-pass, chainable.

**Why (b) is the preferred direction:** matches the user's mental model of `enumerate`, scales to large inputs, and unlocks the same lazy pattern for `zip` (item 2), `map`, `filter`, etc. as a future evolution.

**Why it is gated:** today POOP has **no** user-facing iterator type. The only interaction with iteration is `col.do(block)`; `next()` is banned by `no_iter`; there is no `Iterator` Object. Introducing a single lazy `Enumerate` in isolation would be the only lazy first-class object in the language, with no `next` substitute and only `do(block)` as a useful method — collapsing back to eager behavior on first use.

**Dependency:** **proposal 3** (first-class `Iterator` type). Decide that one first; lazy `Enumerate` falls out naturally as a specific iterator. If proposal 3 is rejected, fall back to shape (a).

**Sketch (assuming proposal 3 is accepted):**

```python
# poop/types/enumerate.py
class Enumerate(Iterator):  # Iterator base from proposal 3
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

**Effort:** small once proposal 3 lands (~30 lines + tests). Without proposal 3: medium and inconsistent (one-off lazy type).

**Decision:** confirm shape (b) lazy `Enumerate` as the target, conditional on proposal 3? Otherwise fall back to shape (a) eager `List`.

### 2. `zip(a, b)` → `a.zip(other)` returning a lazy `Zip` object?

Same dependency tree as item 1: prefer a lazy `Zip(Object)` mirroring Python's `zip` (single-pass, stops at shortest), conditional on proposal 3. Fallback eager shape returns a `List` of `Tuple(item_a, item_b)`.

**Suggested location:** `poop/types/zip.py` (new) plus a hook on `poop/types/_iterable_mixin.py` accepting another iterable.

**Decision:** confirm the lazy shape conditional on proposal 3, with eager `List` fallback otherwise.

### 3. `iter(col)` / `next(it)` → first-class `Iterator` type?

**Today:** iteration only via `col.do(block)` (`INFECTIONS.md:294`).

**Implementation:** invasive — requires a new `Iterator` type in `poop/types/` plus a matching transformer in `poop/transformers/` (just like `Block` has its own).

**Decision:** introduce a first-class iterator, or keep the pure Smalltalk model (only `do`)?

---

## Open decisions — revisit "intentional"

Items currently classified as "no possible substitute" (`INFECTIONS.md:299-345`) but worth reassessing.

### 4. `vars(obj)` → `obj.vars()` returning a `Dict`?

**Today:** bundled into `no_introspection` (`poop/validators/no_introspection.py`, `INFECTIONS.md:312`) alongside `globals()`/`locals()`.

**Important distinction:** `vars(obj)` on an instance returns `__dict__` — that is **instance state**, not lexical scope. POOP uses `__slots__`, so the natural substitute would iterate the slots and produce a `Dict[Str, Object]`.

`globals()`/`locals()` remain without a substitute (they are real lexical scope).

**Decision:** split `vars` out of `no_introspection` and give `Object` a `vars()` substitute?

### 5. `input(prompt)` → introduce a `Console` / `Stdin` type?

**Today:** `INFECTIONS.md:343-345` declares "interactive I/O — no POOP equivalent".

**Note:** Smalltalk *does* model interactive I/O (`Transcript`, etc.). Natural substitute: a POOP `Console` object with `Console.read_line(prompt: Str) -> Str`.

**Scope:** large — a brand new I/O subsystem.

**Decision:** worth the investment, or keep banned?

### 6. `open(path)` → POOP `Path` type inspired by `pathlib`?

**Today:** `INFECTIONS.md:349-351` declares "file I/O — no POOP equivalent".

**Important observation:** the stdlib's `pathlib` is already **object-oriented** — `Path("foo.txt").read_text()`, `Path("dir").iterdir()`, `Path("a").exists()`. The API matches POOP's message-passing model naturally, sparing us a "from-scratch subsystem".

**Possible models:**
- **(a) Wrapper around `pathlib.Path`** — a POOP `Path` wraps `pathlib.Path` and exposes methods like `read_text() -> Str`, `read_lines() -> List[Str]`, `write_text(content: Str) -> Path`, `exists() -> Boolean`, `iterdir() -> List[Path]`. Cheaper, leverages tested pathlib.
- **(b) `Str.open(mode)` returning a POOP `File`** — alternative originally proposed, closer to the builtin `open()` but requires designing the lifecycle from scratch (`close`, context manager via `With`).

**Recommendation:** (a). Pathlib has already done the work of "OO-ifying" filesystem I/O; POOP inherits it almost for free. For `open()` itself, `Path("foo").read_text()` / `write_text()` covers most uses without exposing open file handles.

**Suggested location:** `poop/types/path.py` (new) plus a transformer at `poop/transformers/path.py` to intercept `open(...)` and rewrite it to `Path(...).read_text()` when the pattern is obvious (or simply require users to write `Path("foo").read_text()` directly).

**Scope:** smaller than reimplementing I/O from scratch — wrapper over `pathlib` plus delegating methods.

**Decision:** adopt approach (a) with `pathlib` as the foundation, design `File` from scratch, or keep banned?

### 7. `Slice` as a first-class POOP type?

**Today:** the `slice(...)` builtin is forbidden by `no_slice`; the substitute is the method `obj.slice(start, stop, step)` on each sequence type (`poop/types/{list,tuple,string,bytes,byte_array,range}.py`, `INFECTIONS.md:725-738`). Users cannot construct, store, or pass around a slice as a value — every call site must restate the bounds inline.

**Proposal:** introduce `poop/types/slice.py` defining `Slice(Object)` — a reusable, immutable value object representing a slice range, mirroring Python's `slice()` semantics but in POOP's message-passing style.

**Sketch:**

```python
# poop/types/slice.py
class Slice(Object):
    __slots__ = ("_start", "_stop", "_step")

    def __init__(
        self, start: Int, stop: Int, step: Int | None = None
    ) -> None:
        self._start = start
        self._stop = stop
        self._step = step

    def start(self) -> Int: return self._start
    def stop(self) -> Int: return self._stop
    def step(self) -> Int | None_: return self._step  # POOP None

    def apply_to(self, sequence: _IterableMixin) -> Any:
        # Delegates to the existing per-type .slice() method.
        s = self._step._value if self._step is not None else None
        return sequence.slice(self._start, self._stop, self._step)
```

**Method overload on sequence types:** allow `obj.slice(s)` where `s` is a `Slice` to mean "apply this slice value", in addition to the existing `obj.slice(start, stop, step)` form. Keeps both shapes ergonomic.

**Why it is useful:**
- Reuse: build a slice once, apply it to many collections (`s = Slice(Int(0), Int(5)); a.slice(s); b.slice(s)`).
- Composition: pass slices into functions/blocks as values, store them in `List`s, compare with `==`.
- Mirrors Python's design (`slice` as a real type) without lifting the ban on the free-function `slice(...)`.

**Validator interaction:** `no_slice` keeps forbidding the free `slice(...)` call; users construct via the constructor `Slice(...)` (an `ast.Name` node referring to a POOP-injected name, just like `List`, `Tuple`, etc.), not via the Python builtin. No validator change required — `Slice` is registered in `DEFAULT_NAMESPACE` like other POOP types.

**Open sub-decisions:**
- Negative indices? Python's `slice` allows them; POOP currently inherits Python slice semantics inside `obj.slice(...)`. Carry them forward as-is, or normalize?
- Default `start`/`stop` (Python allows `slice(None, None, 2)`)? Force explicit `Int`s, or accept POOP `None`?
- Should `Slice` be iterable or only applicable? Probably applicable-only, to avoid the lazy-iterator question (which is proposal 3's territory).

**Effort:** small (~40 lines + transformer/namespace registration + tests). **Impact:** restores the value-object flavor of Python's `slice` inside POOP while keeping the free-function ban intact; complementary to the existing method substitute.

**Decision:** introduce `Slice` as a POOP type, or keep the method-only model where slice bounds are always inline?

---

## Open decisions — language semantics

### 8. Smalltalk-style binary operator evaluation (left-to-right, no precedence)?

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

### 9. Audit methods returning `self` — should they mirror Python instead?

**Today:** dozens of POOP methods return `self` for Smalltalk-style cascading. Examples (non-exhaustive):
- `_IterableMixin.do(block) -> Self`
- `Int.real`/`numerator`/`denominator`/`conjugate`/`__ceil__`/`__floor__`/`__trunc__` — all return `self`
- `ByteArray.append`/`clear`/`extend`/`insert`/`remove`/`reverse`/`at_put` — return `self`
- `Set.add`/`discard`/`remove`/`clear`/`update`/`intersection_update`/`difference_update`/`symmetric_difference_update` — return `self`
- `Dict.set`/`update`/`clear` — return `self`
- `List.append`/`extend`/`insert`/`remove`/`clear`/`reverse`/`sort` — return `self`
- `NoneClass.if_not_none` — returns `self`
- `Try.run` / `With.do` — return `self`

**Tension:** the documented principle is *"Method names follow the corresponding Python name — builtins, dunders and collection API"*. But several of those Python counterparts return **`None`**, not the receiver:

| POOP method | Returns | Python equivalent | Returns |
|---|---|---|---|
| `List.append(x)` | `self` | `list.append(x)` | `None` |
| `List.extend(it)` | `self` | `list.extend(it)` | `None` |
| `List.sort()` | `self` | `list.sort()` | `None` |
| `Set.add(x)` | `self` | `set.add(x)` | `None` |
| `Set.update(s)` | `self` | `set.update(s)` | `None` |
| `Dict.update(d)` | `self` | `dict.update(d)` | `None` |
| `ByteArray.append(b)` | `self` | `bytearray.append(b)` | `None` |
| `ByteArray.reverse()` | `self` | `bytearray.reverse()` | `None` |

By naming these methods after their Python counterparts, POOP signals "same semantics" — but the return type silently differs, breaking the mirror.

**Why it matters:**
- A reader who knows Python expects `result = lst.append(x)` to leave `result` as `None`. In POOP they get the list. Either is fine in isolation, but the surprise is in the mismatch.
- Smalltalk-style cascades (`a.append(x).append(y)`) are not idiomatic Python. POOP enables them via `return self` but doesn't mark them as a deliberate diversion from the Python mirror.
- Methods like `Int.real`/`numerator` returning `self` are correct because Python's `int.real` is a property that yields the int — those map cleanly. Mutator methods (`append`, `clear`, etc.) are the genuine divergence.

**Options:**

- **(a) Mirror Python strictly.** All mutators return POOP `none` (mirroring Python's `None`). Cascade chains break; users cascade through explicit `do(block)` if needed. Aligns the rule with the practice.
- **(b) Keep cascading; document explicitly.** Add an explicit principle in `INFECTIONS.md` listing "POOP-Smalltalk extensions to Python's API" — methods that intentionally diverge from the Python mirror by returning `self`. Closes the documentation gap without behavior changes.
- **(c) Hybrid.** Keep `self`-returning for non-mutator/identity methods (e.g., `Int.real`, `NoneClass.if_not_none`); convert mutators to return `none`. Surfaces the principle "mutators are void in Python; POOP follows".

**Scope:** wide — touches every collection mutator and every `Int`/`Float` "identity" property. Each option has different downstream impact on existing examples and tests.

**Effort:** (a) large (audit ~40 methods + update tests/examples). (b) small (just a documentation principle). (c) medium (selective rewrite + principle).

**Decision:** strict mirror (a), document the divergence (b), or hybrid (c)?

### 10. Audit `__slots__` usage on POOP types?

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

---

## Open decisions — documentation

### 11. Audit and rewrite `INFECTIONS.md` to reflect current state?

**Today:** `INFECTIONS.md` (738 lines) is the canonical catalog of validators, transformers, types, and principles. It was written incrementally since the start of the project, and several sections were added when some decisions were still **open questions** ("maybe", "to be defined", "investigate"). Many of those questions have since been settled in practice (in code, tests, commits), but the document may not have been updated uniformly.

**Drift symptoms motivating the audit:**
- Items still classified as "no POOP equivalent" while a substitute exists in practice (e.g.: `vars` — see proposal 4 in this list — a sign that "intentional" turned into inertia).
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

**Effort:** large (line-by-line sweep of 738 lines + cross-check against ~60 validators, ~16 transformers, ~17 types). **Impact:** restores `INFECTIONS.md` as a trustworthy SSOT; prerequisite for proposal 12 (MkDocs) — without a consistent doc, generating the site amplifies the drift.

**Decision:** run the audit in a single pass (large effort but settles it for good), or in incremental waves by section (validators first, then transformers, then types)?

### 12. Documentation site with MkDocs?

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
