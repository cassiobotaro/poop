# Proposals

## Block ↔ callable bridge — foundation + per-namespace consumers landing

The bridge foundation lives in `poop/types/_bridge.py` (`to_python`,
`to_poop`, `bridge(block, *, wrap_args=True, unwrap_return=True)`)
and `Block.__call__` forwards `**kwargs`. Per-namespace consumers
land in their own commits as callers surface.

Shipped consumers:

- **json** — `Json.dumps(default=, cls=, separators=)` and
  `Json.loads(object_hook=, parse_float=, parse_int=, parse_constant=,
  object_pairs_hook=, cls=)`; `JSONEncoder.default(o)` subclassing.
- **tomllib** — `Tomllib.loads/load(parse_float=)`; TOML
  date/time/datetime values land as POOP `Date`/`Time`/`DateTime`.
- **logging** — `Filter` (new) + `Handler` / `Formatter` /
  `StreamHandler` / `NullHandler` / `FileHandler` inherit from
  `_logging.*`; subclass overrides of `filter(record)` / `emit(record)`
  / `format(record)` route through the bridge. `basicConfig` covers
  the full CPython kwarg surface (except `stream`).
- **textwrap** — `textwrap.indent(predicate=)` migrated off its
  local `_bridge_predicate` onto the central helper.
- **difflib** — `SequenceMatcher(isjunk=, autojunk=)`.
- **shutil** — `copytree(ignore=, copy_function=)`, `move(copy_function=)`,
  and `Shutil.ignore_patterns(*patterns)` returns a drop-in `Block`.
- **sqlite3** — `Connection.create_function`, `Connection.create_collation`,
  `Connection.create_aggregate`, `Sqlite3.register_adapter`,
  `Sqlite3.register_converter`. `create_aggregate` accepts a regular
  POOP class with `step`/`finalize` methods; the connection wraps
  them in an internal adapter that bridges args (`to_poop` on step)
  and return (`to_python` on finalize).
- **webbrowser** — `Webbrowser.register(name, constructor=...)`. The
  block returns a `Browser` (or raw `BaseBrowser`); the registry
  layer unwraps to `BaseBrowser` for CPython.
- **os** — new `OS.walk(top, topdown=, onerror=, followlinks=)`
  returning `List[Tuple(Path, List[Str], List[Str])]`; `onerror`
  accepts a `Block`.
- **signal** — `Signal.signal(signum, handler)` accepts a `Block`
  (or `SIG_DFL`/`SIG_IGN` sentinels).
- **pickle** — `Pickler` / `Unpickler` now inherit from `_pickle.*`;
  subclass overrides of `persistent_id(obj)` (Pickler) and
  `persistent_load(pid)` (Unpickler) route through the bridge.
  `Pickler.dispatch_table` accepts POOP `Dict` or Python `dict`;
  each `Block` value is bridged on assignment and stored via the
  parent's C-level descriptor (so the C `save` path sees the bridged
  callables). Reading returns the bridged dict or raises
  `AttributeError` when unset (mirrors CPython's sentinel).
- **difflib.ndiff** — `linejunk=` and `charjunk=` kwargs now route
  through the bridge. (Earlier doc text misattributed this to
  `unified_diff`; the kwarg is actually on `ndiff` / `Differ`.)
- **`to_poop`/`to_python`** now also wrap `bytes`/`bytearray` ↔
  `Bytes`/`ByteArray` (needed by sqlite3 `register_converter`).

All originally pending per-namespace consumers are shipped. New
namespaces should plug callback kwargs / class methods into
`poop.types._bridge.bridge` directly.

Out of scope (now and later): async callbacks (covered by `AsyncIO`),
C-API/ctypes callbacks, full subclassing of stdlib base classes
beyond callback overrides, POOP `LogRecord` wrapper.

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

POOP exposes `Logger`, `Filter`, `Handler` (+ `StreamHandler`,
`NullHandler`, `FileHandler`), `Formatter`, and the basic level
constants. The subclass-extension surface landed: user subclasses
of `Filter` / `Handler` / `Formatter` override `filter(record)` /
`emit(record)` / `format(record)` in POOP idiom (the bridge wraps
the return value). The `record` argument stays as raw
`_logging.LogRecord` — a POOP `LogRecord` wrapper is a separate
follow-up.

Still deferred: `BufferingFormatter`, `Filterer`, `LoggerAdapter`,
the style classes (`PercentStyle`/`StrFormatStyle`/
`StringTemplateStyle`), `Manager`, `RootLogger`, `PlaceHolder`, the
introspection helpers (`getHandlerByName`/`getHandlerNames`/
`getLevelNamesMapping`/`getLogRecordFactory`/`getLoggerClass`),
`captureWarnings`, `makeLogRecord`, `disable`, `exception`, the
dict-config and file-config machinery, and the global toggles
(`logAsyncioTasks`/`logMultiprocessing`/`logProcesses`/`logThreads`/
`raiseExceptions`). All wait for a real caller.

`logging.basicConfig` exposes the full CPython kwarg surface
except `stream` (POOP has no file-object abstraction — write to a
`Path` via `filename`, or wire a custom `Handler`).

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
`configparser.LegacyInterpolation`,
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

### TOML date/time/datetime narrowing + `parse_float` — from the `tomllib` proposal (v0.26.0) — shipped

`tomllib._wrap` now returns POOP `Date` / `Time` / `DateTime` for the
TOML date/time/datetime grammar (previously ISO-8601 `Str`).
`parse_float=` accepts a POOP `Block` routed through `block.bridge`
(default mirrors CPython exactly — Python `float`). Write support
stays out of scope (`tomllib` is read-only upstream).

### `JSONEncoder` / `JSONDecoder` subclassing + advanced kwargs — from the `json` proposal (v0.25.0) — shipped

`cls=`, `default=`, `object_hook=`, `parse_float=`, `parse_int=`,
`parse_constant=`, `object_pairs_hook=`, `separators=` and the
`JSONEncoder` / `JSONDecoder` subclassing surface all landed together
with the Block ↔ callable bridge.

`json.tool` (CLI module) stays out of scope.


