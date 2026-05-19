# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–60 here was fully resolved
across the v1.0.x and v1.1.x cycles:

- Bugs 26–30 → v1.0.1.
- Bug 31 → v1.0.2.
- Leaks 1–11 and signature inconsistencies 12–25 → v1.1.0.
- Items 32–40 → v1.1.1.
- Items 41–45 → v1.1.2.
- Items 46–51 → v1.1.3.
- Items 52–56 → v1.1.4.
- Items 57–60 → v1.1.5 (`is not None` guards in `DateTime.combine`
  and `Lock`/`RLock`/`Semaphore.acquire` now also catch POOP
  `none`; `SSLContext.get_ciphers` wraps the raw `list[dict]`
  return; `Threading._Local.at`/`at_put` annotate `Object` instead
  of `Any`).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
