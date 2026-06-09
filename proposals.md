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

### ~~93. Property-forwarding helper for `_ImplWrapperMixin` types~~ — DONE (as mixins, generator rejected)

Decision: the declarative generator was rejected on inspection —
`logging.py`'s "21 repeated properties" are really four heterogeneous
shapes (plain wrap, optional-`none`, `to_poop` bridge, metaclass
toggles), so a table either covers only ~8 trivial cases or grows
escape hatches, and ty-visibility would force annotation + table
double bookkeeping. The *real* duplication was across classes, and it
shipped as plain mixins with real defs (the proposal-95 pattern):
`_DateFieldsMixin`/`_TimeFieldsMixin` in `datetime.py` (Date/Time/
DateTime shared fields incl. the 11-line `tzinfo` cascade) and
`_VersionMixin`/`_ScopeFlagsMixin`/`_MaskFormsMixin` in
`ipaddress.py` (version ×3, scope flags ×2, mask forms ×2). ~160
duplicated lines now single-sourced; full suite passed unmodified.

### ~~94. Consolidate ad-hoc unwrappers into `_unwrap.py`~~ — DONE

Decision: implemented the slim version. `logging._unwrap_level` was the
only genuine duplication — removed in favour of the already-imported
`_bridge.to_python`. The other three (`fractions._to_python_num`,
`socket._unwrap_address`, `ipaddress._addr_arg`) are legitimate
domain dispatch: each cascade maps different types to `_impl` vs
`_value` vs passthrough (socket's is recursive over `Tuple`), and a
shared duck-typed helper would change edge-case behavior (e.g.
`Fraction(Decimal)`, `Fraction(Boolean)`). Kept as-is by design.

### ~~95. Logger level-method mixin~~ — DONE

Decision: `_LevelMethodsMixin` (real defs, ty-visible — no class-body
loop) now carries `debug`/`info`/`warning`/`error`/`critical`/`log`/
`setLevel`, shared by `Logger` and `LoggerAdapter`. `exception` stays
Logger-only (adding it to LoggerAdapter would be an API change) and
the `Logging` static forwarders keep their module-function shape.

### ~~96. `collections` infection~~ — DONE

Decision: `Counter` (Smalltalk `Bag`), `deque` (`OrderedCollection`),
`defaultdict` (factory as a block — no bridging needed), `OrderedDict`
(a reordering `Dict` subclass), `namedtuple` (class factory returning
a `Tuple` subclass with property fields), and `ChainMap` (live lookup
chain over `Dict`s — pulled in when a caller asked) shipped in
`poop/types/collections.py` + namespace-only
`poop/transformers/collections.py`. Entry points keep Python's exact
casing. Remaining tail (`UserDict`/`UserList`/`UserString` —
subclassing helpers with no POOP use case; `collections.abc` — exists
for isinstance checks, against the philosophy) is out of scope.

### ~~97. `functools` infection~~ — SUPERSEDED by #103

Original framing (PascalCase `Partial` entry point, caching deferred
without a path) was replaced by a fresh maintainer-requested entry;
see #103.

### ~~98. `itertools` as messages on iterables~~ — REJECTED (implemented, then reverted)

Maintainer decision: the mixin earns a message when it **substitutes a
forbidden construct** — `reduce` exists because the comprehension/
accumulation idiom it replaces is banned. The itertools combinators
substitute nothing forbidden and are derivable from the existing
message surface (`map`/`filter`/`zip`/`enumerate`/`reduce`), so they
add API weight without philosophical payoff. Shipped in `016b099`,
reverted in full.

### ~~99. `base64` namespace~~ — WITHDRAWN

The premise was wrong: base64 is already fully infected as **messages on
the value** — `Bytes` carries 9 encoder/decoder variants each
(b16/b32/b32hex/b64/standard_b64/urlsafe_b64/a85/b85/z85, including the
`altchars` kwarg), `Str` carries the decoders (see `poop/types/bytes.py`
and the MIGRATION.md "Base64" section). A namespace mirror would be
strictly less idiomatic than what exists. Nothing to do.

### ~~100. `Object.subclass_responsibility()`~~ — REJECTED (implemented, then reverted)

Maintainer decision: the Python way to mark abstract methods is the
`@abstractmethod` decorator; POOP follows Python idioms where one
exists (the same principle behind `map` not `collect`), so a
Smalltalk-only message is not wanted. Shipped in `cecf271`, reverted
in full. If abstract-method support is ever desired, it should arrive
through a decorator story instead.

### ~~101. Source-line caret in validation errors~~ — DONE

Decision: `_format_error` in `poop/cli.py` appends the offending
source line in a numbered gutter plus a `^` at the column when the
error carries position info (`ValidationError` gets line + caret,
`ExecutionError` line only). Both the run path and `--validators-only`
use it; errors without position keep the old one-line form.

### ~~102. REPL meta-commands~~ — DONE

Decision: `:methods <expr>` (evaluates a variable or safe literal
through the transformer pipeline, so `"abc"` answers `Str`'s messages,
and lists the non-underscored surface), `:explain <construct>` (runs a
minimal snippet through the validators and prints their own messages —
explanations can never drift from the rejection text), and `:help`.
Lines starting with `:` are intercepted before the normal pipeline.

### 103. `functools` infection

**What exists today.** No `functools` namespace — user code referencing
`functools` gets `NameError` (verified by execution). The only trace is
internal: `_iterable_mixin.py` imports `functools.reduce` to power the
`col.reduce(init, block)` message. Requested by the maintainer
(pull-when-asked).

**Proposal.** Namespace-only infection following the `queue`/`heapq`
precedent: a lowercase `functools` mirror exposing, with Python's exact
casing (all lowercase in CPython):

- `partial(block, *args, **kwargs)` — a call-transparent POOP type
  wrapping `functools.partial`; also bound as a direct entry point.
  Useful when the frozen args are computed values, where a `lambda`
  closure would capture variables late.
- `cmp_to_key(block)` — adapts a two-argument comparison block for the
  `key=` parameters the sorting messages already accept.
- `reduce(block, iterable, init)` — module mirror for parity; docs point
  to `col.reduce(init, block)` as the idiomatic message form.
- `cache(block)` / `lru_cache(block, maxsize=none)` — applied as
  **explicit wrapper calls on blocks** (`cached = functools.cache(block)`),
  not as decorators; no decorator story required. Memoized callables
  stay call-transparent.

**Scope.** New transformer + `functools.py` type module + tests +
INFECTIONS.md + MIGRATION.md recipes + CLAUDE.md lists.

## Resolved

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
