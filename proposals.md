# Proposals

No open design proposals. The post-v0.54 engineering backlog from the
expert code review (refactors A3, C1, C2, C4; coverage T2, T3;
declined C5) and the v0.55.0 signature-audit sweep (param-mismatch
retroactive fix; audit noise filter; decision preservation) both
shipped on `main`.

## v0.6.0 stdlib expansion backlog — from the signature audit (v0.55.0)

`docs/signature-audit.md` triaged 779 findings against 84 stdlib
mirrors. 127 rows are sanctioned divergences (closed); the remaining
652 are `defer-v0.6.0` — names CPython exposes that POOP currently
curates out. Below they are regrouped into proposal-shaped chunks so
each one can be picked up independently. The audit doc remains the
canonical per-row inventory; this section adds the rationale and
expected scope per area.

### POSIX low-level surface (`os` 204, `sys` 57, `signal` 8, `resource` 1, `gc` 6, `pwd` 1, `grp` 1, `pstats` 10)

POOP's `os` is a thin curated wrapper: it relies on `Path` for file
I/O and exposes only the environment / cwd / process-info methods.
Everything fd-based (`os.open`, `dup`, `dup2`, `pipe`, `read`,
`write`, `close`, `closerange`, `fdopen`), the `exec*` family
(`execv*`, `execl*`, `posix_spawn*`), the `fork`/`waitpid`/`spawn*`
process-control surface, scheduling helpers (`sched_*`), and the
permission helpers (`chmod`, `chown`, `chroot`, `umask`) all stay
deferred until a real caller surfaces. POOP would either have to
mirror the fd integer ABI (uncomfortable — fds are not `Path`) or
invent a `FileDescriptor` POOP type; pick the path when a user
forces the choice.

`sys` defers everything that requires Python-level introspection
(`getframe`, `getrefcount`, `gettrace`, `settrace`, `setprofile`,
`audit`, `addaudithook`, `_getframe`, `_current_frames`,
`monitoring`). The hooks integrate with CPython's frame model, which
POOP intentionally hides. Defer until a debugger or profiler that
needs them lands.

`signal` defers `set_wakeup_fd`, `siginterrupt`, `sigwait`,
`pthread_sigmask`, `sigwaitinfo`, `sigtimedwait` (advanced async
signal handling). `gc` defers `get_referents`/`get_referrers`,
`get_stats`, `set_debug` (introspection). `pwd.getpwall` and
`grp.getgrall` defer (rarely needed). `pstats` defers everything
except `Stats` (the SortKey enum, helpers like `add`, `print_callees`).

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

### TLS / SSL (`ssl` 33)

POOP currently exposes `SSLContext` with the most-used surface and
the verify-mode / protocol constants. Deferred: the `Purpose` /
`Options` / `VerifyFlags` / `VerifyMode` enums (currently passed
as raw `Int`), the `HAS_*` capability constants
(`HAS_SSLv2`/`HAS_TLSv1`/`HAS_TLSv1_3`/etc.), the legacy protocol
constants (`PROTOCOL_SSLv23`/`PROTOCOL_TLSv1*`), `MemoryBIO`,
`SSLObject`, `SSLSession`, the cert-conversion helpers
(`DER_cert_to_PEM_cert` / `PEM_cert_to_DER_cert` /
`get_server_certificate`), `enum_certificates` /
`enum_crls`, and the per-error error-number constants
(`SSLErrorNumber`, `AlertDescription`). Expose as a single
extension when a real TLS-server or low-level cert use case
surfaces.

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

### Calendar output formatters (`calendar` 24)

`Calendar` and the module-level `month`/`calendar` strings are
exposed. Deferred: `HTMLCalendar`, `LocaleHTMLCalendar`,
`LocaleTextCalendar`, `TextCalendar` (more specific output
formatters than the plain functions), the `Day`/`Month` enums,
`mdays`, `prcal`, `prmonth`, `prweek`, `_localized_day` /
`_localized_month` private helpers. Ship as a "calendar
formatting" mini-proposal when an HTML/Locale caller surfaces.

### Codec registry (`codecs` 27)

POOP doesn't expose the registry surface at all (`register`,
`lookup`, `lookup_error`, `register_error`, `unregister`). The
incremental encoder/decoder protocol (`IncrementalEncoder`,
`IncrementalDecoder`, `BufferedIncrementalEncoder`,
`BufferedIncrementalDecoder`, `StreamReader`, `StreamWriter`,
`StreamReaderWriter`, `StreamRecoder`, `EncodedFile`) and the base
`Codec` class are also out. Codec-customisation is a niche surface;
defer until someone needs to wire a custom encoder.

### Enum subclasses (`enum` 14)

`Enum` / `IntEnum` / `StrEnum` / `Flag` / `IntFlag` / `auto` are
exposed. Deferred: `EnumDict`, `EnumType`, `EnumMeta`, `EJECT`,
`KEEP`, `CONFORM`, `STRICT`, `member`, `nonmember`, `global_enum`,
`property` (the enum-specific descriptor), `verify`, `unique`,
`pickle_by_enum_name`, `pickle_by_global_name`. Most are Py3.11+
extension hooks — defer until used.

### Threading / concurrency primitives (`threading` 11, `queue` 1, `timeit` 6)

POOP exposes `Thread`, `Lock`, `RLock`, `Event`, `Semaphore`,
`Barrier`. Deferred from `threading`: `Condition`, `BoundedSemaphore`,
`Timer`, `local`, `excepthook`, `get_native_id`, `main_thread`,
`stack_size`, `_dangling`, `setprofile_all_threads`,
`settrace_all_threads`. `queue` defers `ShutDown` (Py 3.13+). The
`timeit` deferrals (`Timer.print_exc`, `default_number`,
`reindent`, `template`) are private/internal.

### Date / time / zone extras (`time` 9, `datetime` 2, `zoneinfo` 1)

POOP's `time` / `datetime` / `zoneinfo` cover the daily-use surface.
Deferred: `time.clock_*` family (`clock_gettime`, `clock_settime`,
`clock_getres`, etc. — POSIX-only), `time.thread_time*`,
`time.pthread_getcpuclockid`, `datetime.MAXYEAR` /
`datetime.MINYEAR` constants (intentionally hidden behind
the `Date` type's range checks), `zoneinfo.reset_tzpath`. Most
need a real per-system caller before they land.

### Network / SQL / decimal extras (`socket` 13, `sqlite3` 8, `decimal` 9)

`socket` defers `getaddrinfo`, `getnameinfo`, `getfqdn`,
`gethostname`, `if_indextoname`, `if_nametoindex`, `if_nameindex`,
`SocketType`, the address-family + protocol introspection helpers.
`sqlite3` defers the `Blob` type, `enable_callback_tracebacks`,
`register_adapter` / `register_converter`, `complete_statement`,
`Cache`, `Statement`. `decimal` defers the special-context flags
(`Underflow`, `Overflow`, `Subnormal`, `Rounded`, `Inexact`,
`Clamped`, `DivisionImpossible`, `FloatOperation`,
`InvalidContextError`).

### Pickle classes (`pickle` 9)

POOP exposes the four module-level functions but not the
`Pickler` / `Unpickler` classes themselves, the
`PickleBuffer` type, the `PickleError` /
`PicklingError` / `UnpicklingError` hierarchy individually,
`HIGHEST_PROTOCOL`, `DEFAULT_PROTOCOL`. Adding the classes
unblocks subclass-customisation (custom `persistent_id`,
`dispatch_table`, etc.).

### Webbrowser controllers (`webbrowser` 16)

POOP exposes `open`/`open_new`/`open_new_tab`/`get` plus a single
`Browser` wrapper. Deferred: every named-browser controller class
(`Chrome`, `Chromium`, `Edge`, `Mozilla`, `Opera`, `Konqueror`,
`Epiphany`, `Elinks`, `BackgroundBrowser`, `GenericBrowser`,
`UnixBrowser`), and the `register` / `register_*_browsers` entry
points. The deferred-`webbrowser.register` proposal under "Future
work" already covers the registration story; the controller
classes ship as part of the same change.

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

### `async for` / `async with` / async generators — from the async-ban decision (v0.52.0)

v0.52.0 dropped `NoAsyncValidator` so `async def` methods and `await`
expressions now pass the pipeline. The async-flavoured control
structures stayed banned by their existing validators (`async for` by
`no_loops`, `async with` by `no_with`, async generators indirectly via
`no_yield`). Lifting any of these requires a separate decision plus
likely a new POOP-side idiom (`do`-style iteration over async
iterables, `With` adapter for async context managers, etc.). Deferred
until a concrete caller surfaces.

### `Random.getstate()` / `Random.setstate(state)` — from the `random` proposal (v0.7.0)

Python's `random.Random.getstate()` returns a tuple of the form
`(version, internal_state, gauss_next)` where `internal_state` is a
**625-element tuple of ints** carrying the Mersenne Twister state.
POOP's type discipline forbids leaking raw Python primitives across
the namespace boundary, but wrapping every state int into a POOP
`Int` is pure overhead — nobody inspects the state; it exists only
to round-trip into `setstate`. The cleanest path requires either an
opaque-state POOP type that pickles/unpickles via Bytes, or a
sanctioned divergence allowing the raw tuple through (the user never
sees what's inside).

For v1, `.seed(a, version)` covers the 95% case of determinism. The
state pair is deferred until a concrete user need surfaces — at
which point the trade-off (opaque-Bytes type vs. raw-tuple
divergence) can be decided with real requirements in hand.

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

### `copy.replace` and `deepcopy(obj, memo)` — from the `copy` proposal (v0.19.0)

Two deferrals from v0.19.0:

- **`copy.replace(obj, /, **kwargs)`** (Python 3.13+) — a shortcut
  for "build a new instance with these field updates" on
  dataclasses / NamedTuple / classes that implement `__replace__`.
  POOP classes don't use decorators (no `dataclasses` story), and
  `__replace__` is a recent addition; defer until a real caller
  surfaces.
- **`deepcopy(obj, memo)`** — the `memo` parameter is a CPython
  implementation detail (an `id(obj)`-keyed dict tracking
  recursive identities during traversal). It has no clean type-
  discipline mapping because POOP `Dict` keys are POOP `Object`,
  not `int`. v0.19.0 ships `deepcopy(obj)` without `memo`; callers
  needing custom memoization should implement `__deepcopy__` on
  their POOP class instead.

### `webbrowser.register` — from the `webbrowser` proposal (v0.16.0)

v0.16.0 ships the read paths (`open`/`open_new`/`open_new_tab`/`get`)
plus the `Error` exception class and the `Browser` wrapper around
`webbrowser.BaseBrowser`. `webbrowser.register(name, constructor,
instance=None, *, preferred=False)` is deferred because the
`constructor` argument is a Python callable returning a
`BaseBrowser` subclass instance — there is no clean POOP
type-discipline mapping for "callable that returns a Browser" in
v1. When a real caller surfaces, decide whether to accept a POOP
`Block` returning a `Browser` (and unwrap internally) or fold this
into a richer factory API.

### Optional base64 kwargs — from the `base64` proposal (v0.13.0)

v0.13.0 ships the 9 encoders + 9 decoders that mirror `base64.*` with
their Python defaults. Optional kwargs are deferred: `altchars` and
`validate` on `b64encode`/`b64decode`, `casefold` and `map01` on
`b32decode`/`b32hexdecode`/`b16decode`, `foldspaces`/`wrapcol`/`pad`/
`adobe` on `a85encode`, `foldspaces`/`adobe`/`ignorechars` on
`a85decode`, and `pad` on `b85encode`. None of these affect the
common case (encoding/decoding with stdlib defaults); when a real
caller surfaces, add the kwargs to the relevant `Bytes`/`Str` methods
and update the type discipline note to allow `Bytes`/`Str` for any
non-bool flag.

Legacy file-oriented helpers (`base64.encode`, `decode`,
`encodebytes`, `decodebytes`) are intentionally out of scope — POOP
routes file I/O through `Path`.

### `GetPassWarning` — from the `getpass` proposal (v0.11.0)

Python's `getpass.GetPassWarning` is emitted (not raised) when the
echo-suppression call fails on the underlying TTY. It is a
`UserWarning` subclass surfaced via the `warnings` module — a model
POOP does not have (see `warnings` in INFECTIONS.md's "Stdlib
coverage" tables: "out").
v0.11.0 ships `getpass.getpass` and `getpass.getuser` but does not
expose `GetPassWarning`; the underlying CPython call still emits the
warning to stderr, POOP user code just cannot catch or filter it.

A proper exposure would require either (a) a POOP `Warning`/`Stream`
story to mirror `warnings.filterwarnings` and friends, or (b)
upgrading the warning to a raised `Error` and letting POOP's `Try`
catch it — diverging from Python's actual behavior. Deferred until
a concrete user need surfaces.

