# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–84 here was fully resolved
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
- Items 83–84 → v1.1.16 (`Int.pow` accepts an optional modulus for
  modular exponentiation; `Math.floor`/`ceil`/`trunc` accept
  `Decimal`/`Fraction` via a `_unwrap_num` helper that routes
  `_impl` into the stdlib protocol).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
