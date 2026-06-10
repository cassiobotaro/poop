# Proposals

No open design proposals.

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
- The June 2026 repository-survey backlog (90–103) closed → v1.5.0.
  Shipped: `no_type`/`no_help` validators (90–91); collection-
  transformer factory, cross-class property mixins, unwrap and logger
  consolidation (92–95); the full `collections` infection — `Counter`,
  `deque`, `defaultdict`, `OrderedDict`, `namedtuple`, `ChainMap`
  (96); source-line caret diagnostics in the CLI (101); REPL
  `:methods`/`:explain`/`:help` meta-commands (102); the `functools`
  infection — `partial`, `cmp_to_key`, `reduce`, decorator-free
  `cache`/`lru_cache` (97 → 103). Rejected after trial, reverted in
  full: itertools combinators as iterable messages (98 — they
  substitute no forbidden construct) and
  `Object.subclass_responsibility()` (100 — Python's idiom is the
  `@abstractmethod` decorator). Withdrawn: `base64` namespace (99 —
  already shipped as `Bytes`/`Str` messages).

- Pull-when-asked batch (maintainer request): `Date.min`/`Date.max`
  class attributes (bare `MINYEAR`/`MAXYEAR` stay out per the existing
  permanent divergence); collections tail — `deque`
  `insert`/`index`/`copy`/`+`/`*`, namedtuple
  `_fields`/`_make`/`_asdict`/`_replace`, seeded
  `defaultdict`/`OrderedDict` constructors; functools tail —
  `cache_info()`/`cache_clear()` on memoized blocks and
  `partialmethod` (`wraps`/`singledispatch`/`total_ordering` stay out:
  decorator machinery / type dispatch). The json "deferred" note was
  stale — subclassing and all callback kwargs had already shipped via
  `block.bridge`; INFECTIONS.md corrected. Second sweep: base64 gained
  `a85decode` kwargs and full kwarg parity on the `Str` decoders;
  `Shlex` gained the `punctuation_chars` read property (its remaining
  gaps — `eof`, `sourcehook`, parser internals — reclassified as
  out-by-design); both stale "deferred" notes corrected. Pending next
  release.

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
