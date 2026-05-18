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

### Misc one-offs (`array`, `copy`, `email`, `ipaddress`, `json`, `pprint`, `profile`, `pwd`, `queue`, `resource`, `smtplib`, `statistics`, `subprocess`, `weakref`, `platform`)

Tracked individually in the audit doc; no grouping advantage. Pull
when a caller forces the question.
