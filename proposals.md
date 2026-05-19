# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–31 here was fully resolved
across the v1.0.x cycle:

- Bugs 26–30 → v1.0.1 (Slice None handling, _kwargs_from filter,
  DictItems non-pair guard, Enumerate start normalization, Try
  double-execution).
- Bug 31 → v1.0.2 (no_unary_minus narrowed to numeric literals).
- Leaks 1–11 and signature inconsistencies 12–25 → v1.1.0 (a sweep
  through sys/decimal/subprocess/logging/asyncio/concurrent/codecs/
  signal/csv plus the `_IteratorBase` generic and several
  `NoneClass` widenings).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks):
file an issue with a concrete use case to surface a deferred name.
