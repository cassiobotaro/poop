# Proposals

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

### Logging framework (`logging`)

Still deferred: `BufferingFormatter`, `Filterer`, `LogRecord` (a POOP
wrapper around `_logging.LogRecord` — overrides currently receive the
raw stdlib record), `LoggerAdapter`, the style classes
(`PercentStyle`/`StrFormatStyle`/`StringTemplateStyle`), `Manager`,
`RootLogger`, `PlaceHolder`, the introspection helpers
(`getHandlerByName`/`getHandlerNames`/`getLevelNamesMapping`/
`getLogRecordFactory`/`getLoggerClass`), `captureWarnings`,
`makeLogRecord`, `disable`, `exception`, the dict-config and
file-config machinery, and the global toggles
(`logAsyncioTasks`/`logMultiprocessing`/`logProcesses`/`logThreads`/
`raiseExceptions`). All wait for a real caller. `basicConfig(stream=)`
also stays out — POOP has no file-object abstraction; use a
custom `Handler` or `filename=`.

### Archive format extras (`zipfile`, `tarfile`, `gzip`)

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

### Codec registry (`codecs`)

POOP doesn't expose the registry surface at all (`register`,
`lookup`, `lookup_error`, `register_error`, `unregister`). The
incremental encoder/decoder protocol (`IncrementalEncoder`,
`IncrementalDecoder`, `BufferedIncrementalEncoder`,
`BufferedIncrementalDecoder`, `StreamReader`, `StreamWriter`,
`StreamReaderWriter`, `StreamRecoder`, `EncodedFile`) and the base
`Codec` class are also out. Codec-customisation is a niche surface;
defer until someone needs to wire a custom encoder.

### Date / time / zone extras (`time`, `datetime`, `zoneinfo`)

POOP's `time` / `datetime` / `zoneinfo` cover the daily-use surface.
Deferred: `time.clock_*` family (`clock_gettime`, `clock_settime`,
`clock_getres`, etc. — POSIX-only), `time.thread_time*`,
`time.pthread_getcpuclockid`, `datetime.MAXYEAR` /
`datetime.MINYEAR` constants (intentionally hidden behind
the `Date` type's range checks), `zoneinfo.reset_tzpath`. Most
need a real per-system caller before they land.

### Network / SQL extras (`socket`, `sqlite3`)

`socket` defers `getaddrinfo`, `getnameinfo`, `getfqdn`,
`gethostname`, `if_indextoname`, `if_nametoindex`, `if_nameindex`,
`SocketType`, the address-family + protocol introspection helpers.
`sqlite3` defers the `Blob` type, `complete_statement`, `Cache`,
`Statement`, `enable_callback_tracebacks` (debug helper).

### Pickle extras

`PickleBuffer` (out-of-band buffer protocol for zero-copy pickle)
stays deferred — niche use case.

### Text & data helpers (`string`, `textwrap`, `shlex`, `re`, `difflib`, `unicodedata`, `random`, `hmac`, `uuid`, `fnmatch`)

A pile of small one-off defers across text-processing namespaces:
`string.capwords`, `string.whitespace`, `string.printable`;
`textwrap.dedent`; `shlex.SHLEX_NEWLINE`; `re.purge`, `re.template`,
`re.NOFLAG`; `difflib.HtmlDiff`, `Differ`, `IS_CHARACTER_JUNK` (as
a public class attr — used internally as the `ndiff` default);
`random.SystemRandom`; `hmac.compare_digest`, `hmac.digest`,
`hmac.new`; `uuid.SafeUUID`; `fnmatch.translate` extras. Each can
be added one-at-a-time when a caller asks.

### File / config / I/O extras (`shutil`, `configparser`, `tempfile`, `glob`, `io`, `filecmp`, `mimetypes`)

POOP curates these around `Path`. Deferred:
`shutil.{disk_usage,sameopenfile,sameopenstat,specialbits,...}`,
`configparser.LegacyInterpolation`,
`configparser.MAX_INTERPOLATION_DEPTH`, `tempfile.tempdir`,
`tempfile.SpooledTemporaryFile`, `glob.has_magic`,
`glob.has_magic_chars`, `glob.tab_completion_glob`, `io.IOBase` and
the buffered-base classes, `filecmp.DEFAULT_IGNORES`,
`mimetypes.knownfiles`, etc. Surface piecemeal.

### Misc one-offs (`array`, `copy`, `email`, `ipaddress`, `json`, `pprint`, `profile`, `pwd`, `queue`, `resource`, `smtplib`, `statistics`, `subprocess`, `weakref`, `platform`)

Tracked individually in the audit doc; no grouping advantage. Pull
when a caller forces the question.
