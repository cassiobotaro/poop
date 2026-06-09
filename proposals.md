# Proposals

## Open proposals

Backlog from the June 2026 repository survey (philosophy gaps verified by
execution; duplication figures verified by inspection). Suggested order:
90–91 first (small, restore language consistency), then 92/94/95 (low-risk
internal refactors), 96 and 98 as the highest-value features, and
93/97/99–102 on demand.

### ~~90. `no_type` validator~~ — DONE

Decision: `type()` rejected via `make_call_name_validator`; message points
to `obj.class_name()` and polymorphism. Implemented with registration,
tests, INFECTIONS.md entry, and a MIGRATION.md recipe.

### ~~91. `no_help` validator~~ — DONE

Decision: `help()` rejected via `make_call_name_validator` — interactive
escape hatch, no POOP equivalent. Implemented with registration, tests,
and an INFECTIONS.md entry.

### ~~92. Collection-transformer factory~~ — DONE

Decision: shared machinery extracted to
`poop/transformers/_collection.py` — a ClassVar-driven
`CollectionRewriter` base (statically subclassable, ty-friendly) plus
`make_constructor`/`make_iterable_from`/`wrap_elts`; dict and frozenset
keep only their genuinely specific converters. 359 → 291 lines, zero
behavior change (full suite passed unmodified).

### 93. Property-forwarding helper for `_ImplWrapperMixin` types

**What exists today.** Wrapper types declare long runs of properties that
only re-wrap an `_impl` attribute — e.g. `poop/types/logging.py` has 21
properties of the shape `return Str(self._impl.name)`; `datetime.py` and
`ipaddress.py` follow the same pattern.

**Proposal.** A declarative helper (table of `attr → wrapper type`) that
generates the forwarding properties. Caveat to resolve in design: generated
properties must stay visible to `ty` as statically typed attributes — if that
forces type-stub gymnastics, the readability cost may not be worth it; the
proposal is to prototype on `logging.py` first and decide.

**Scope.** One helper in the type layer + adoption in 2–3 wrapper modules.

### 94. Consolidate ad-hoc unwrappers into `_unwrap.py`

**What exists today.** Several modules re-implement coercion that belongs
beside the shared `_unwrap` helpers: `_to_python_num` in
`poop/types/fractions.py`, `_unwrap_address` in `poop/types/socket.py`,
`_addr_arg` in `poop/types/ipaddress.py`, `_unwrap_level` in
`poop/types/logging.py`.

**Proposal.** Move/merge these into `poop/types/_unwrap.py` as typed thin
aliases (the established pattern there), leaving only genuinely
domain-specific dispatch in the owning modules.

**Scope.** `_unwrap.py` + the four modules above; no behavior change.

### 95. Logger level-method mixin

**What exists today.** `poop/types/logging.py` writes the five level methods
(`debug`/`info`/`warning`/`error`/`critical`) three times — on `Logger`, on
`LoggerAdapter`, and as module-level forwarders — ~15 near-identical methods.

**Proposal.** Generate them from a single level table (mixin or class-body
loop), keeping signatures and return types identical.

**Scope.** `logging.py` only; existing tests must pass unchanged.

### 96. `collections` infection

**What exists today.** No `collections` transformer or types —
`Counter`, `deque`, `defaultdict`, `namedtuple`, `OrderedDict` are
unreachable from POOP programs. This is the stdlib gap with the strongest
Smalltalk affinity: `Counter` ≈ `Bag`, `deque` ≈ `OrderedCollection`.

**Proposal.** Namespace-only infection following the established pattern
(lowercase `collections` mirror + PascalCase entry points `Counter`, `Deque`,
`DefaultDict`, `NamedTuple`, `OrderedDict`), with POOP types wrapping each.

**Scope.** New transformer + type module(s) + tests + INFECTIONS.md; large
but mechanical, following the `queue`/`heapq` precedent.

### 97. `functools` infection

**What exists today.** No `functools` namespace. Note `reduce` already exists
as a message — `_iterable_mixin.py:52` — so the proposal is narrower than the
Python module.

**Proposal.** Namespace with `Partial` (a POOP type wrapping
`functools.partial`, call-transparent) and `cmp_to_key`. Caching decorators
(`lru_cache`, `cache`) deferred until a decorator story exists (custom
decorators are currently impossible — free functions are forbidden).

**Scope.** New transformer + `functools.py` type module + tests +
INFECTIONS.md.

### 98. `itertools` as messages on iterables

**What exists today.** No `itertools` surface. A free-function-style
namespace mirror (`itertools.pairwise(col)`) would fight the message-passing
philosophy.

**Proposal.** Implement the useful combinators as messages on
`_IterableMixin` instead: `.pairwise()`, `.batched(n)`, `.chain(other)`,
`.accumulate(block)`, `.product(other)`, `.combinations(n)`,
`.permutations(n)`. Each returns the appropriate POOP collection/iterator
type.

**Scope.** `_iterable_mixin.py` + iterator/collection types + tests +
INFECTIONS.md + MIGRATION.md recipes (`itertools.x(col)` → `col.x()`).

### 99. `base64` namespace

**What exists today.** Already flagged as deferred in INFECTIONS.md (the
optional-kwargs tail). No namespace exists, so even the core surface is
unreachable.

**Proposal.** Namespace-only infection exposing the core encode/decode
surface (`b64encode`/`b64decode`, `b32`, `b16`, `urlsafe_*`) over POOP
`Bytes`/`Str`. Optional kwargs (`altchars`, `validate`, `casefold`) stay
deferred per the pull-when-asked policy.

**Scope.** New transformer + `base64.py` type module + tests +
INFECTIONS.md.

### 100. `Object.subclass_responsibility()`

**What exists today.** No way to mark a method as abstract: `abc` is not
infected, and decorator syntax has no story. Smalltalk's native idiom is
`self subclassResponsibility`.

**Proposal.** Add `subclass_responsibility()` to `Object`
(`poop/types/object.py`), raising a POOP error naming the receiver's class
and the calling method — an abstract-method idiom with no new syntax,
truer to Smalltalk than wrapping `ABCMeta`.

**Scope.** `object.py` + tests + INFECTIONS.md + possibly a Template Method
example update in `examples/patterns/`.

### 101. Source-line caret in validation errors

**What exists today.** `poop/cli.py:20-21` prints `poop: <message> (line N,
col M)`. The offending source line is never shown, although `PoopError`
already carries `lineno`/`col_offset`.

**Proposal.** Rust-style diagnostics: print the source line followed by a
`^` marker at the column. Applies to both single-error mode and
`--validators-only` (which lists all errors).

**Scope.** `poop/cli.py` (and the error-formatting path in `poop/errors.py`
if formatting belongs there) + CLI tests.

### 102. REPL meta-commands

**What exists today.** The REPL (`poop/repl.py`) has history and tab
completion but no exploration commands; discovering an object's messages
requires `obj.dir()` knowledge, and a rejected construct gives no pointer to
its rationale.

**Proposal.** Colon-prefixed meta-commands, Smalltalk-browser-flavored:
`:methods <expr>` lists the messages an object understands;
`:explain <construct>` maps a validator rejection (e.g. `if`, `len`) to its
INFECTIONS.md rationale and the idiomatic substitute.

**Scope.** `poop/repl.py` + a validator→rationale table + REPL tests.

## Resolved

The leak/signature/bug audit logged as 1–89 here was fully resolved
across the v1.0.x and v1.1.x cycles:

The leak/signature/bug audit logged as 1–89 here was fully resolved
across the v1.0.x and v1.1.x cycles:

- Bugs 26–30 → v1.0.1.
- Bug 31 → v1.0.2.
- Leaks 1–11 and signature inconsistencies 12–25 → v1.1.0.
- Items 32–40 → v1.1.1.
- Items 41–45 → v1.1.2.
- Items 46–51 → v1.1.3.
- Items 52–56 → v1.1.4.
- Items 57–60 → v1.1.5.
- Map/Filter/Zip/Enumerate one-shot → v1.1.6.
- Item 64 → v1.1.7.
- Item 65 → v1.1.8.
- Items 66–67 → v1.1.9.
- Item 68 → v1.1.10.
- Items 69–70 → v1.1.11.
- Items 71–73 → v1.1.12.
- Coverage lifted above 95% → v1.1.13.
- Items 74–79 → v1.1.14.
- Items 80–82 → v1.1.15.
- Items 83–84 → v1.1.16.
- Items 85–86 → v1.1.17.
- Item 87 → v1.1.18.
- Item 88 → v1.1.19.
- Item 89 → v1.1.20 (`Dict` gains `__or__` and `__ior__` for PEP 584
  shallow merge — `d1 | d2` returns a new `Dict`, `d1 |= d2` mutates
  in place, both isinstance-guarded).
- Examples reorganized into `basics/`, `idiomatic/`, and `patterns/`
  subfolders → v1.1.21.
- Doc consistency fixes (INFECTIONS.md `Dict views` path prefixes,
  MIGRATION.md `zoneinfo.TZPATH` described as attribute, not callable)
  → v1.1.22.
- GoF pattern catalogue completed — examples for the 16 remaining
  patterns (Factory Method, Abstract Factory, Builder, Prototype,
  Singleton, Adapter, Bridge, Facade, Flyweight, Proxy, Chain of
  Responsibility, Command, Interpreter, Iterator, Mediator, Memento)
  added to `examples/patterns/` → v1.1.23.
- Non-GoF OO pattern examples added — Specification (Evans/Fowler),
  Money value object (Fowler), and Execute Around Method (Beck) in
  `examples/patterns/` → v1.1.24.
- Internal-quality refactoring batch (no user-facing change): the
  `_ImplWrapperMixin` (now returning `Self`) adopted across the 11
  wrapper modules that hand-wrote `_from_impl`; a `to_boolean()` helper
  in `boolean.py` replacing the 253 `true if X else false` ternaries
  spread over the type layer; transformer failures wrapped in a new
  `TransformError` so every pipeline stage surfaces a domain error; and
  `_kwargs_from` applied to the remaining pure optional-kwarg blocks
  (`Struct`/`StructNamespace.unpack_from`, `NormalDist.quantiles`).
  Pending next patch release.

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
