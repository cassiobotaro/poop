# Proposals

## v0.6.0 stdlib expansion backlog

The v0.55.0 signature-audit pass surfaced 652 CPython names that POOP
currently curates out. They are regrouped below into proposal-shaped
chunks so each area can be picked up independently when a real caller
surfaces.

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

### Text & data helpers — difflib leftovers

`difflib.HtmlDiff` and `difflib.Differ` (as a subclassable POOP
class, plus exposing `IS_CHARACTER_JUNK` as a public class attribute
rather than the internal `ndiff` default).

### Misc one-offs (`array`, `copy`, `email`, `ipaddress`, `json`, `pprint`, `profile`, `pwd`, `queue`, `resource`, `smtplib`, `statistics`, `subprocess`, `weakref`, `platform`)

Tracked individually in the audit doc; no grouping advantage. Pull
when a caller forces the question.
