# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–73 here was fully resolved
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
- Items 71–73 → v1.1.12 (`ConfigParser.get*` accept `vars` and enforce
  keyword-only; `TemporaryDirectory` / `NamedTemporaryFile` gain
  `delete` / `delete_on_close`; `LogRecord.created` / `Gc.get_threshold`
  / `Gc.get_count` / `Sqlite3.Row.at` tighten `-> Any` to POOP types).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
