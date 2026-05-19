# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–67 here was fully resolved
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
- Item 64 (Dict.pop without default raises KeyError) → v1.1.7.
- Item 65 (Range.__iter__ annotation) → v1.1.8.
- Items 66–67 (Int.__pow__ returns Float; Bz2/Lzma open follow Gzip
  pattern) → v1.1.9.

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
