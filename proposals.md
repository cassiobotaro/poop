# Proposals

No open design proposals. The post-v0.54 engineering backlog from the
expert code review (refactors A3, C1, C2, C4; coverage T2, T3;
declined C5) and the v0.55.0 signature-audit sweep (retroactive
Default kwarg policy + sanctioned-divergence triage) both shipped on
`main`.

## v0.6.0 stdlib expansion backlog

The v0.55.0 signature-audit pass surfaced 652 CPython names that POOP
currently curates out. They are regrouped below into proposal-shaped
chunks so each area can be picked up independently when a real caller
surfaces.

### POSIX low-level surface (`os`, `sys`, `signal`, `gc`, `pwd`, `grp`) — minus the parts marked out forever

The fd-based I/O / `exec*` / `fork`+`spawn*` / `sys` frame-and-audit hooks moved to INFECTIONS.md§Permanent-divergences-from-CPython. What remains here is the surface POOP could still wrap when a caller asks:

- `signal.siginterrupt`, `signal.sigwait`, `signal.pthread_sigmask`, `signal.sigwaitinfo`, `signal.sigtimedwait` — synchronous signal-wait helpers (no fd dependency).
- `pwd.getpwall`, `grp.getgrall` — listing variants.
- `pstats` — the `SortKey` enum and `Stats.add`/`.print_callees`/etc. Pair with the `profile` proposal if it ever expands.
- `os` permission helpers (`chmod`, `chown`, `chroot`, `umask`) — Path-compatible already; could surface on `Path` rather than on the `os` namespace.

### Logging framework (`logging` 35)

POOP exposes `Logger`, `Handler`, `Formatter`, and the basic level
constants. Deferred: `BufferingFormatter`, `Filter` / `Filterer`,
`LogRecord`, `LoggerAdapter`, the style classes
(`PercentStyle`/`StrFormatStyle`/`StringTemplateStyle`), `Manager`,
`RootLogger`, `PlaceHolder`, the introspection helpers
(`getHandlerByName`/`getHandlerNames`/`getLevelNamesMapping`/
`getLogRecordFactory`/`getLoggerClass`), `captureWarnings`,
`makeLogRecord`, `disable`, `exception`, the dict-config and
file-config machinery, and the global toggles
(`logAsyncioTasks`/`logMultiprocessing`/`logProcesses`/`logThreads`/
`raiseExceptions`). Most of these need POOP subclass-extension
surface (custom Filters/Handlers/Formatters) — pair with the
"subclassing" decision below.

`logging.basicConfig` is also a `param-mismatch` row: POOP exposes
two of its ~17 kwargs (`level`, `format`). Expanding to the full
set (`filename`, `filemode`, `datefmt`, `style`, `handlers`,
`force`, `encoding`, `errors`, `stream`) ships together with the
Handler/Filter wrappers.

### Archive format extras (`zipfile` 24, `tarfile` 17, `gzip` 2)

POOP exposes `ZipFile` / `TarFile` / `GzipFile` with the read /
write / extract surface. Deferred items are mostly the low-level
machinery: `PyZipFile`, `ZipExtFile`, the `LZMACompressor` /
`LZMADecompressor` re-exports under `zipfile`, the struct format
constants (`structCentralDir`/`structFileHeader`/etc.), the
TarFile error subclasses (`InvalidHeaderError`,
`SubsequentHeaderError`, `TruncatedHeaderError`,
`EOFHeaderError`, `EmptyHeaderError`, `LinkFallbackError`), and
the encoding helpers (`itn`/`nti`/`stn`/`nts`/`calc_chksums`).
Most are CPython internals. The `zstd` module export from `zipfile`
needs its own wrapping decision.

### Codec registry (`codecs` 27)

POOP doesn't expose the registry surface at all (`register`,
`lookup`, `lookup_error`, `register_error`, `unregister`). The
incremental encoder/decoder protocol (`IncrementalEncoder`,
`IncrementalDecoder`, `BufferedIncrementalEncoder`,
`BufferedIncrementalDecoder`, `StreamReader`, `StreamWriter`,
`StreamReaderWriter`, `StreamRecoder`, `EncodedFile`) and the base
`Codec` class are also out. Codec-customisation is a niche surface;
defer until someone needs to wire a custom encoder.

### Date / time / zone extras (`time` 9, `datetime` 2, `zoneinfo` 1)

POOP's `time` / `datetime` / `zoneinfo` cover the daily-use surface.
Deferred: `time.clock_*` family (`clock_gettime`, `clock_settime`,
`clock_getres`, etc. — POSIX-only), `time.thread_time*`,
`time.pthread_getcpuclockid`, `datetime.MAXYEAR` /
`datetime.MINYEAR` constants (intentionally hidden behind
the `Date` type's range checks), `zoneinfo.reset_tzpath`. Most
need a real per-system caller before they land.

### Network / SQL extras (`socket` 13, `sqlite3` 8)

`socket` defers `getaddrinfo`, `getnameinfo`, `getfqdn`,
`gethostname`, `if_indextoname`, `if_nametoindex`, `if_nameindex`,
`SocketType`, the address-family + protocol introspection helpers.
`sqlite3` defers the `Blob` type, `enable_callback_tracebacks`,
`register_adapter` / `register_converter`, `complete_statement`,
`Cache`, `Statement`.

### Pickle classes (`pickle` 9)

POOP exposes the four module-level functions but not the
`Pickler` / `Unpickler` classes themselves, the
`PickleBuffer` type, the `PickleError` /
`PicklingError` / `UnpicklingError` hierarchy individually,
`HIGHEST_PROTOCOL`, `DEFAULT_PROTOCOL`. Adding the classes
unblocks subclass-customisation (custom `persistent_id`,
`dispatch_table`, etc.).

### Text & data helpers (`string` 3, `textwrap` 1, `shlex` 1, `re` 4, `difflib` 5, `unicodedata` 1, `random` 5, `hmac` 3, `uuid` 2, `getpass` 4, `fnmatch` 1)

A pile of small one-off defers across text-processing namespaces:
`string.capwords`, `string.whitespace`, `string.printable`;
`textwrap.dedent`; `shlex.SHLEX_NEWLINE`; `re.purge`, `re.template`,
`re.NOFLAG`; `difflib.context_diff`, `difflib.unified_diff`,
`difflib.HtmlDiff`, `Differ`, `IS_CHARACTER_JUNK`;
`random.SystemRandom`; `hmac.compare_digest`, `hmac.digest`,
`hmac.new`; `uuid.SafeUUID`; `getpass.GetPassWarning` (already
captured under "Future work"); `fnmatch.translate` extras. Each can
be added one-at-a-time when a caller asks.

### File / config / I/O extras (`shutil` 10, `configparser` 6, `tempfile` 2, `glob` 3, `io` 6, `filecmp` 2, `mimetypes` 3)

POOP curates these around `Path`. Deferred:
`shutil.{disk_usage,sameopenfile,sameopenstat,specialbits,...}`,
`shutil.ignore_patterns`, `configparser.LegacyInterpolation`,
`configparser.MAX_INTERPOLATION_DEPTH`, `tempfile.tempdir`,
`tempfile.SpooledTemporaryFile`, `glob.has_magic`,
`glob.has_magic_chars`, `glob.tab_completion_glob`, `io.IOBase` and
the buffered-base classes, `filecmp.DEFAULT_IGNORES`,
`mimetypes.knownfiles`, etc. Surface piecemeal.

### Misc one-offs (`array` 1, `copy` 3, `email` 2, `ipaddress` 2, `json` 1, `pprint` 1, `profile` 2, `pwd` 0, `queue` 0, `resource` 0, `smtplib` 2, `statistics` 5, `subprocess` 1, `weakref` 6, `platform` 11)

Tracked individually in the audit doc; no grouping advantage. Pull
when a caller forces the question.

---

## Future work

Items deferred from shipped proposals that need their own follow-up
once a prerequisite exists.

### TOML date/time/datetime narrowing + `parse_float` — from the `tomllib` proposal (v0.26.0)

v0.26.0 ships `tomllib.loads`/`load` with full POOP-type round-trip
for everything except date/time/datetime, which **flatten to ISO-8601
`Str`** as a transient divergence — POOP doesn't yet have a `DateTime`
type. When the `datetime` proposal lands, `tomllib._wrap` tightens to
return a `DateTime` POOP type for these values; tests will need a
small update.

`parse_float` kwarg also deferred — the proposal mentions a Python
callable defaulting to `Float`, but routing TOML floats into
`Decimal` (the documented motivation) pairs with the `decimal`
proposal landing first. Write support stays out of scope (`tomllib`
is read-only upstream).

### `JSONEncoder` / `JSONDecoder` subclassing + advanced kwargs — from the `json` proposal (v0.25.0)

v0.25.0 ships `json.dumps`/`loads`/`dump`/`load` with round-trip POOP
type discipline plus the common formatting flags (`skipkeys`,
`ensure_ascii`, `check_circular`, `allow_nan`, `indent`,
`sort_keys`) and `json.JSONDecodeError` for use with `Try.except_`.

Deferred:
- **`JSONEncoder` / `JSONDecoder` classes** — POOP doesn't yet
  expose enough subclassing surface to let users override
  `.default(obj)` or `.object_hook` and have it dispatch through the
  unwrap/wrap layer cleanly.
- **`cls=...` / `default=` / `object_hook=` / `parse_float=` /
  `parse_int=` / `parse_constant=` / `object_pairs_hook=` /
  `separators=`** — callback hooks that need POOP `Block` →
  Python `callable` adaptation with type discipline still preserved.

`json.tool` (CLI module) stays out of scope.

### Streaming-lexer extras on `Shlex` — from the `shlex` proposal (v0.23.0)

v0.23.0 ships the module-level functions (`split`/`join`/`quote`)
and a `Shlex` class with `.get_token()`, iteration, and the
`.lineno`/`.whitespace_split` properties. The full CPython surface
(`.read_token`, `.sourcehook`, the configurable character-class
attributes `.commenters`/`.wordchars`/`.whitespace`/`.escape`/
`.quotes`/`.escapedquotes`/`.escapedquotes`, plus `.infile`/`.source`/
`.debug`/`.token`/`.error_leader`/`.push_token`/`.push_source`/
`.pop_source`) is deferred until a real caller needs it. Adding
each of these is a small additional method or property delegating
to `self._impl`.


