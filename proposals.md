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

## Open decisions — semantics

### 1. Should `.map()` / `.filter()` be lazy like Python's `map`/`filter`?

**Today:** `_IterableMixin.map`/`filter`/`filter_false`
(`poop/types/_iterable_mixin.py:36-43`) materialize eagerly via
`self._collect(...)`. `_collect` is overridden per type
(`List._collect`, `Tuple._collect`, `Set._collect`,
`FrozenSet._collect`), so `List(...).map(f) -> List`,
`Set(...).map(f) -> Set`, `Tuple(...).map(f) -> Tuple` — the
receiver's type is preserved. Types without an override (Range,
Bytes, ByteArray, MemoryView, Enumerate, Zip) fall through to the
mixin default which returns a `List`.

This matches **Smalltalk's `collect:`** (type-preserving, eager) but
diverges from **Python's `map(...)` / `filter(...)` builtins**, which
return a lazy iterator regardless of input type.

**Tension:** the project's banner phrasing is "Python interpreter
infected by Smalltalk". When in doubt the recent direction has been
"mirror Python". `map`/`filter` are one of the most visible places
where that mirror breaks.

**Possible models:**

- **(a) Keep eager + type-preserving (status quo).** Document
  explicitly that POOP's `.map()` is `collect:`, not Python's `map`.
  Pro: simple, predictable, chains nicely (`set.map(f).sum()`),
  matches what the 4 example files already do
  (`examples/statistics.py`, `examples/pipeline.py`,
  `examples/grades.py`, `examples/common_interests.py`). Con: large
  iterables materialize eagerly; surprises a reader who comes from
  Python and expects lazy.

- **(b) Switch to lazy.** `.map()` and `.filter()` return a new
  `Map` / `Filter` POOP type wrapping a lazy iterator (mirroring
  `Enumerate`/`Zip`, which already exist as lazy iterator types).
  Output type is no longer the receiver's type.
  Pro: matches Python; memory-friendly for big inputs; `Path.glob()`
  / `iterdir()` could plug into the same model. Con: breaks the
  Smalltalk-like type-preservation; `set.map(f)` no longer returns a
  Set; existing `data.map(f).sum()` works only if `Map` exposes
  `sum()` (likely via `_IterableMixin`); side-effects in `block` now
  happen per-consumer instead of once.

- **(c) Hybrid.** Keep eager `.map()` (preserving today's contract)
  and add lazy `.lazy_map()` / `.lazy_filter()` for the big-data
  case. Or rename one of the pair (e.g. eager becomes `.collect()`,
  lazy is `.map()`). Pro: no breakage; user explicitly opts into
  laziness. Con: two near-identical APIs; documentation cost; choice
  fatigue.

**Notes for any choice:**
- Python's `map(...)` / `filter(...)` builtins are blocked by
  `no_map`/`no_filter` validators today. That stays — the user
  always goes through the method.
- `_IterableMixin` inheritance means changing `.map()` ripples
  through `List`/`Tuple`/`Set`/`FrozenSet`/`Range`/`Bytes`/
  `ByteArray`/`MemoryView`/`Enumerate`/`Zip`. ~35 references in
  examples and tests would need an audit.
- A `Map`/`Filter` type would itself want to inherit
  `_IterableMixin` so `data.map(f).filter(g).sum()` keeps chaining.
- `find` / `reduce` / `sum` / `min` / `max` / `all` / `any` already
  consume the iterator once and don't depend on `_collect`, so they
  work the same in both worlds.
- A `do(block) -> none` is the eager forcing primitive; in a lazy
  world the user calls `.do(...)` to materialize side-effects.

**Recommendation:** lean toward **(b)** if "mirror Python" is the
guiding principle, accepting the migration cost in examples/tests.
**(c)** is a softer landing if the migration scares. Avoid **(a)**
unless we explicitly decide POOP is "Python with Smalltalk
collections" rather than "mirror Python".

**Scope (b):** new `poop/types/map.py` and `poop/types/filter.py`
(mirroring `enumerate.py`/`zip.py`), update mixin to return them,
audit ~35 call sites in examples/tests for places that depend on
type preservation (e.g. `Set.map(f)` where the user later does set
ops).

**Decision:** which model? If (b), is the breaking change
acceptable on a pet project (no external users)?
