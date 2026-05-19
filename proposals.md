# Proposals

No open design proposals.

The leak/signature/bug audit logged as 1–51 here was fully resolved
across the v1.0.x and v1.1.x cycles:

- Bugs 26–30 → v1.0.1 (Slice None handling, _kwargs_from filter,
  DictItems non-pair guard, Enumerate start normalization, Try
  double-execution).
- Bug 31 → v1.0.2 (no_unary_minus narrowed to numeric literals).
- Leaks 1–11 and signature inconsistencies 12–25 → v1.1.0 (a sweep
  through sys/decimal/subprocess/logging/asyncio/concurrent/codecs/
  signal/csv plus the `_IteratorBase` generic and several
  `NoneClass` widenings).
- Items 32–40 → v1.1.1 (a follow-up audit closing optional-param
  gaps on `Dict.pop`, `List.pop`, `Str.split/rsplit/count/find/
  index/rfind/rindex/strip/lstrip/rstrip` and `Bytes.count/find/
  index/rfind/rindex`; `__rmul__` on `List/Tuple/Bytes/ByteArray`;
  and the `html.entities` map shape).
- Items 41–45 → v1.1.2 (sibling-extension sweep finishing what
  v1.1.1 started: `maxsplit` on `Bytes/ByteArray.split/rsplit`;
  `start`/`end` on `ByteArray.count/find/index/rfind/rindex`;
  `start`/`end` on `startswith`/`endswith` and `count` on
  `replace` across all three text wrappers; plus
  `Ipaddress.get_mixed_type_key` wrapping its tuple return).
- Items 46–51 → v1.1.3 (10-agent partitioned sweep — six survivors
  from ~30 raw findings: Boolean wrapping on `ZipInfo.is_dir`,
  `Lzma.is_check_supported`, `ZipFile.allowZip64`, and
  `TarFile.list.verbose`; `-> Boolean` annotations on the
  `Decimal.is_finite` predicate family; `NoneClass` widening on
  `String.capwords`, `Array.pop`, and `Range.__init__`; plus
  `Gzip.compress` / `Gzip.open` realigned to the `Bz2` / `Zlib`
  optional-default pattern).

Long-tail per-namespace tail items follow the
[pull-when-asked policy](INFECTIONS.md#pull-deferred-surface-only-when-a-caller-asks):
file an issue with a concrete use case to surface a deferred name.
