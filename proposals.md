# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–56 here was fully resolved
across the v1.0.x and v1.1.x cycles:

- Bugs 26–30 → v1.0.1.
- Bug 31 → v1.0.2.
- Leaks 1–11 and signature inconsistencies 12–25 → v1.1.0.
- Items 32–40 → v1.1.1.
- Items 41–45 → v1.1.2.
- Items 46–51 → v1.1.3.
- Items 52–56 → v1.1.4 (DateTime/Time tzinfo wrap ZoneInfo;
  `-> Boolean` annotations on `Fraction` / `DateTime` /
  `_AddressBase` comparison ops; `NoneClass` widening on
  `ByteArray.pop`, `Fraction.__init__`,
  `Fraction.limit_denominator`, `Math.perm`, `CMath.log`;
  hardcoded `Int(N)` defaults realigned to the `_opt_int` /
  `_is_absent` pattern on `Binascii`, `Calendar`, `Math.prod`,
  `Threading.Condition.notify`; `Shlex.error_leader.lineno` /
  `infile` and `Shlex.debug` setter tightened from `Any`).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks).
