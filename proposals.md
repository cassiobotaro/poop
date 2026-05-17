# Proposals

## Expose `threading` as POOP messages

Python's `threading` provides preemptive multitasking primitives:
`Thread`, locks, events, conditions, semaphores, barriers.

**Proposal — `threading` (lowercase module) + class set:**

1. **`Thread` class** — `Thread(target=None, name=None, args=(), kwargs=None, *, daemon=None)`,
   `.start()`, `.join(timeout=None)`, `.is_alive() -> Boolean`,
   `.name -> Str`, `.ident -> Int | NoneClass`,
   `.native_id -> Int`, `.daemon -> Boolean`.
2. **Synchronisation primitives:** `Lock`, `RLock`, `Condition`,
   `Semaphore`, `BoundedSemaphore`, `Event`, `Barrier`, `Timer`.
   Each context-manager friendly via `With`.
3. **Module-level helpers:** `threading.current_thread() -> Thread`,
   `threading.main_thread() -> Thread`,
   `threading.active_count() -> Int`,
   `threading.enumerate() -> List[Thread]`,
   `threading.get_ident() -> Int`,
   `threading.get_native_id() -> Int`,
   `threading.local() -> Local`,
   `threading.settrace(func)`, `threading.setprofile(func)`,
   `threading.stack_size(size=None) -> Int`.
4. **`Local` class** for thread-local storage.

**Type discipline:** POOP types end-to-end; locks/events are POOP
objects with messages instead of Python primitives.

**Out of scope (for v1):** `threading.excepthook` interception
(introspection-adjacent).

## Expose `multiprocessing` as POOP messages

Python's `multiprocessing` is the parallel-process counterpart to
`threading`. Large surface — this proposal scopes v1 to the most
common entry points.

**Proposal — `multiprocessing` (lowercase module) + class set:**

1. **`Process` class** mirroring `Thread`'s shape:
   `Process(target=None, name=None, args=(), kwargs=None, *, daemon=None)`,
   `.start()`, `.join(timeout=None)`, `.is_alive()`, `.terminate()`,
   `.kill()`, `.close()`, `.pid -> Int | NoneClass`, `.exitcode -> Int | NoneClass`.
2. **Inter-process primitives:** `Pipe(duplex=True) -> Tuple[Connection, Connection]`,
   `Queue(maxsize=0) -> Queue`, `SimpleQueue() -> SimpleQueue`,
   `JoinableQueue(maxsize=0) -> JoinableQueue`,
   `Lock()`, `RLock()`, `Condition(lock=None)`, `Semaphore(value=1)`,
   `BoundedSemaphore(value=1)`, `Event()`, `Barrier(parties, action=None, timeout=None)`,
   `Value(typecode, *args, lock=True) -> Value`,
   `Array(typecode_or_type, size_or_initializer, *, lock=True) -> Array`.
3. **`Pool` class** for worker pools:
   `Pool(processes=None, initializer=None, initargs=(), maxtasksperchild=None)`,
   `.apply(func, args=(), kwds={}) -> result`,
   `.apply_async(...) -> AsyncResult`,
   `.map(func, iterable, chunksize=None) -> List`,
   `.map_async(...) -> AsyncResult`,
   `.imap`, `.imap_unordered`, `.starmap`, `.starmap_async`,
   `.close`, `.terminate`, `.join`.
4. **Manager** via `multiprocessing.Manager() -> SyncManager` for
   shared-state objects across processes.
5. **Helpers:** `multiprocessing.cpu_count()`,
   `multiprocessing.current_process()`,
   `multiprocessing.parent_process()`,
   `multiprocessing.active_children() -> List[Process]`,
   `multiprocessing.get_context(method=None) -> Context`,
   `multiprocessing.set_start_method(method, force=False)`,
   `multiprocessing.get_start_method(allow_none=False)`,
   `multiprocessing.freeze_support()`.

**Type discipline:** POOP types end-to-end; child-process IPC
preserves type identity through pickling.

**Out of scope (for v1):**

- `multiprocessing.shared_memory` (3.8+) — niche.
- `multiprocessing.dummy` — duplicates `threading` with the same
  API.

## Expose `concurrent` as POOP messages

Python's `concurrent.futures` provides high-level
parallelism via Executors + Future objects. Cleaner than raw
threads/processes for embarrassingly parallel work.

**Proposal — `concurrent.futures` (lowercase namespace) + class set:**

1. **Executor classes:** `ThreadPoolExecutor(max_workers=None, thread_name_prefix='', initializer=None, initargs=())`,
   `ProcessPoolExecutor(max_workers=None, mp_context=None, initializer=None, initargs=(), *, max_tasks_per_child=None)`,
   `InterpreterPoolExecutor(...)` (3.14+ if it lands).
2. **Executor instance methods:** `.submit(fn, *args, **kwargs) -> Future`,
   `.map(fn, *iterables, timeout=None, chunksize=1) -> Map`,
   `.shutdown(wait=True, *, cancel_futures=False)`. Context manager
   friendly via `With`.
3. **`Future` class:** `.result(timeout=None) -> Object`,
   `.exception(timeout=None) -> Error | NoneClass`,
   `.cancel() -> Boolean`, `.cancelled() -> Boolean`,
   `.done() -> Boolean`, `.running() -> Boolean`,
   `.add_done_callback(fn)`.
4. **Module helpers:**
   `concurrent.futures.wait(fs, timeout=None, return_when=ALL_COMPLETED) -> Tuple[Set[Future], Set[Future]]`,
   `concurrent.futures.as_completed(fs, timeout=None) -> Map[Future]`.
5. **Constants:** `FIRST_COMPLETED`, `FIRST_EXCEPTION`,
   `ALL_COMPLETED`.
6. **Errors:** `CancelledError`, `TimeoutError`,
   `BrokenExecutor`, `InvalidStateError`,
   `BrokenThreadPool`, `BrokenProcessPool`.

**Type discipline:** Futures wrap whatever POOP type the callable
returns; `Object` is the generic ceiling.

## Expose `subprocess` as POOP messages

Python's `subprocess` launches and communicates with child
processes. Critical for shelling out to external tools.

**Proposal — `subprocess` (lowercase module) + class set:**

1. **High-level `run`:** `subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, capture_output=False, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, text=None, env=None, universal_newlines=None, **other_popen_kwargs) -> CompletedProcess`.
2. **Backward-compat shortcuts:**
   `subprocess.call(args, ...) -> Int`,
   `subprocess.check_call(args, ...) -> Int`,
   `subprocess.check_output(args, ...) -> Bytes | Str`,
   `subprocess.getoutput(cmd, *, encoding=None, errors=None) -> Str`,
   `subprocess.getstatusoutput(cmd, *, encoding=None, errors=None) -> Tuple[Int, Str]`.
3. **`Popen` class** — full lifecycle: `.communicate(input=None, timeout=None)`,
   `.wait(timeout=None)`, `.poll()`, `.terminate()`, `.kill()`,
   `.send_signal(sig)`, `.stdin`/`.stdout`/`.stderr`,
   `.pid -> Int`, `.returncode -> Int | NoneClass`, `.args`.
4. **`CompletedProcess` class** — `.args`, `.returncode`, `.stdout`,
   `.stderr`, `.check_returncode()`.
5. **Constants:** `subprocess.DEVNULL`, `PIPE`, `STDOUT`.
6. **Errors:** `SubprocessError`, `CalledProcessError`,
   `TimeoutExpired`.

**Type discipline:** `args` as `List[Str]` (POOP idiomatic — no
`shell=True` by default), `Bytes`/`Str` for I/O streams, `Path`
for `cwd`.

**Out of scope (for v1):**

- `shell=True` mode is permitted but discouraged (injection risk);
  document but don't restrict at validator level.

## Expose `queue` as POOP messages

Python's `queue` provides synchronised FIFO/LIFO/priority queues
between threads.

**Proposal — `queue` (lowercase module) + class set:**

1. **Queue classes:** `Queue(maxsize=0)` (FIFO),
   `LifoQueue(maxsize=0)` (LIFO),
   `PriorityQueue(maxsize=0)` (heap-based),
   `SimpleQueue()` (lightweight FIFO without `task_done`/`join`).
2. **Shared instance methods:**
   `.put(item, block=True, timeout=None) -> NoneClass`,
   `.put_nowait(item)`,
   `.get(block=True, timeout=None) -> element`,
   `.get_nowait()`,
   `.task_done() -> NoneClass`,
   `.join() -> NoneClass`,
   `.qsize() -> Int`,
   `.empty() -> Boolean`, `.full() -> Boolean`.
3. **Errors:** `Empty`, `Full`, `ShutDown` (3.13+).

**Type discipline:** POOP types for queued elements; `Int` for
queue sizes; `Boolean` for predicates.

## Audit the rest of the Python stdlib for POOP equivalents

The same question that drove the `math` namespace (shipped in
v0.6.0) applies to every other commonly-used Python module: imports
are forbidden in POOP, so anything in the stdlib is currently
unreachable from POOP code. Each module needs a decision about
whether — and how — to surface it inside POOP, without breaking the
message-passing model.

Three Smalltalk patterns are already in use and should guide the
decision case-by-case:

- **Message on the value** — when the operation belongs to a single
  receiver (`'abc'.is_digit()`, `path.read_text()`,
  `bytes.b64encode()`, `coll.sort()`).
- **Class-with-class-methods (`math`-style namespace global)** — when
  the operation parses, creates, or combines values (`Random new`,
  `Date today`, `NeoJSONReader fromString:`, `math.atan2`). In POOP
  this maps to a namespace-only binding like `Try` / `With` / `Path`.
- **Specialized global object** — when there is no single value to
  receive the message (`Smalltalk exit`, `Transcript`, `SystemVersion
  current`). POOP would split this into responsibility-scoped objects
  like `System`, `Platform`, `Stdout`, `Stderr` rather than a single
  monolithic `Sys`.

The audit should classify each commonly-used module against these
three patterns, producing a per-module proposal (or a "stays out"
note). Below is the full stdlib (`sys.stdlib_module_names`, 194
top-level modules, private `_*` modules excluded) grouped by the
categories from
[docs.python.org/3/library](https://docs.python.org/3/library/),
each annotated with one of:

- **covered** — already reachable from POOP today.
- **proposed** — has an active proposal in this file.
- **audit** — needs a decision (own proposal or "stays out").
- **out** — won't be surfaced; reason in the sketch column.

### Text Processing Services

| Module | Status | Sketch |
|---|---|---|
| `string` | covered | `string` + `Template` (shipped in this PR) |
| `re` | covered | `re` + `Pattern` + `Match` (shipped in v0.29.0) |
| `difflib` | covered | `difflib` + `SequenceMatcher` (shipped in this PR) |
| `textwrap` | covered | `textwrap` + `TextWrapper` (shipped in this PR) |
| `unicodedata` | covered | `unicodedata` namespace (shipped in this PR) |
| `stringprep` | out | Internal IDNA helper |
| `readline` | out | REPL infrastructure — POOP doesn't expose a REPL |
| `rlcompleter` | out | REPL infrastructure |

### Binary Data Services

| Module | Status | Sketch |
|---|---|---|
| `struct` | covered | `struct` + `Struct` (shipped in this PR) |
| `codecs` | covered | `codecs` + `CodecInfo` (shipped in this PR) |

### Data Types

| Module | Status | Sketch |
|---|---|---|
| `datetime` | covered | `datetime` + `Date` + `Time` + `DateTime` + `TimeDelta` + `TimeZone` (shipped in v0.32.0) |
| `zoneinfo` | covered | `zoneinfo` + `ZoneInfo` (shipped in this PR) |
| `calendar` | covered | `calendar` + `Calendar` (shipped in this PR) |
| `collections` | covered | `OrderedDict` / `Counter` / `deque` redundant — POOP collections carry the methods |
| `heapq` | covered | `heapq` namespace + `HeapMerge` (shipped in v0.22.0) |
| `bisect` | covered | `bisect` namespace (shipped in v0.21.0) |
| `array` | covered | `array` + `Array` (shipped in this PR) |
| `weakref` | covered | `weakref` + `WeakRef` + `WeakSet` + `WeakKeyDictionary` + `WeakValueDictionary` (shipped in this PR) |
| `types` | out | Introspection — forbidden in POOP |
| `copy` | covered | `copy` namespace (shipped in v0.19.0) |
| `pprint` | covered | `pprint` + `PrettyPrinter` (shipped in v0.20.0) |
| `reprlib` | out | POOP forbids `repr` |
| `enum` | covered | `enum` + `Enum` + `IntEnum` + `StrEnum` + `Flag` + `IntFlag` + `ReprEnum` (shipped in this PR) |
| `graphlib` | covered | `graphlib` + `TopologicalSorter` (shipped in v0.28.0) |

### Numeric and Mathematical Modules

| Module | Status | Sketch |
|---|---|---|
| `numbers` | out | ABC hierarchy — POOP has its own type tree |
| `math` | covered | `Math` namespace (shipped in v0.6.0) |
| `cmath` | audit | Needs `Complex` POOP type story — see "Future work" |
| `decimal` | covered | `decimal` + `Decimal` + `Context` (shipped in v0.32.0) |
| `fractions` | covered | `fractions` + `Fraction` (shipped in this PR) |
| `random` | covered | `Random` namespace (shipped in v0.7.0) |
| `statistics` | covered | `statistics` + `NormalDist` (shipped in this PR) |

### Functional Programming Modules

| Module | Status | Sketch |
|---|---|---|
| `itertools` | covered | Mixin methods on iterables |
| `functools` | covered | `coll.reduce(…)`; partial application via `Block` |
| `operator` | out | Reflective access — clashes with no-introspection rule |

### File and Directory Access

| Module | Status | Sketch |
|---|---|---|
| `pathlib` | covered | `Path` |
| `os.path` / `posixpath` / `ntpath` / `genericpath` / `nturl2path` | covered | Reachable via `Path` |
| `fileinput` | out | Niche CLI helper |
| `stat` | out | Low-level constants — `Path` already exposes the queries |
| `filecmp` | covered | `filecmp` + `Dircmp` (shipped in this PR) |
| `tempfile` | covered | `tempfile` + `TemporaryFile` + `NamedTemporaryFile` + `SpooledTemporaryFile` + `TemporaryDirectory` (shipped in this PR) |
| `glob` | covered | `glob` namespace + `GlobIter` (shipped in v0.17.0) |
| `fnmatch` | covered | `fnmatch` namespace (shipped in v0.18.0) |
| `linecache` | out | Internal traceback helper |
| `shutil` | covered | `shutil` namespace (shipped in this PR) |

### Data Persistence

| Module | Status | Sketch |
|---|---|---|
| `pickle` | covered | `pickle` + `Pickler` + `Unpickler` (shipped in this PR) |
| `copyreg` | out | Internal hook for `pickle` |
| `shelve` | out | Depends on `dbm` |
| `marshal` | out | CPython internal |
| `dbm` | out | Niche; prefer `sqlite3` |
| `sqlite3` | covered | `sqlite3` + `Connection` + `Cursor` + `Row` (shipped in this PR) |

### Data Compression and Archiving

| Module | Status | Sketch |
|---|---|---|
| `zlib` | covered | `zlib` + `Compress` + `Decompress` (shipped in this PR) |
| `gzip` | covered | `gzip` + `GzipFile` (shipped in this PR) |
| `bz2` | covered | `bz2` + `BZ2File` + `BZ2Compressor` + `BZ2Decompressor` (shipped in this PR) |
| `lzma` | covered | `lzma` + `LZMAFile` + `LZMACompressor` + `LZMADecompressor` (shipped in this PR) |
| `zipfile` | covered | `zipfile` + `ZipFile` + `ZipInfo` (shipped in this PR) |
| `tarfile` | covered | `tarfile` + `TarFile` + `TarInfo` (shipped in this PR) |
| `compression` | covered | `compression` umbrella (shipped in this PR) |

### File Formats

| Module | Status | Sketch |
|---|---|---|
| `csv` | covered | `csv` + `Reader` + `Writer` + `DictReader` + `DictWriter` + `Sniffer` (shipped in this PR) |
| `configparser` | covered | `configparser` + `ConfigParser` + `RawConfigParser` (shipped in this PR) |
| `tomllib` | covered | `tomllib` namespace (shipped in v0.26.0) |
| `netrc` | out | Niche legacy format |
| `plistlib` | out | macOS-specific niche |

### Cryptographic Services

| Module | Status | Sketch |
|---|---|---|
| `hashlib` | covered | `hashlib` + `Hash` (shipped in this PR) |
| `hmac` | covered | `hmac` + `HMAC` (shipped in v0.27.0) |
| `secrets` | covered | `secrets` namespace (shipped in v0.12.0) |

### Generic Operating System Services

| Module | Status | Sketch |
|---|---|---|
| `os` | covered | `os` / `process` / `env` namespaces (v0.49.0) |
| `io` | covered | `io` / `StringIO` / `BytesIO` namespaces (v0.49.0) |
| `time` | covered | `time` / `StructTime` namespaces (v0.49.0) |
| `logging` | covered | `logging` / `Logger` / `Handler` / `Formatter` namespaces (v0.49.0) |
| `argparse` | out | POOP programs don't expose a CLI surface (yet) |
| `getpass` | covered | `getpass` namespace (shipped in v0.11.0) |
| `curses` | out | Terminal UI — niche |
| `platform` | covered | `platform` / `Uname` namespaces (v0.49.0) |
| `errno` | covered | `errno` namespace (shipped in v0.10.0) |
| `ctypes` | out | FFI — clashes with introspection rules |
| `mmap` | out | Low-level; defer until needed |

### Concurrent Execution

| Module | Status | Sketch |
|---|---|---|
| `threading` | proposed | See proposal above |
| `multiprocessing` | proposed | See proposal above |
| `concurrent` | proposed | See proposal above |
| `subprocess` | proposed | See proposal above |
| `sched` | out | Niche scheduler |
| `queue` | proposed | See proposal above |
| `contextvars` | out | Implementation detail |

### Networking and Interprocess Communication

| Module | Status | Sketch |
|---|---|---|
| `asyncio` | covered | `asyncio` / `Future` namespaces — `async def` source forbidden (v0.48.0) |
| `socket` | covered | `socket` + `Socket` namespaces (v0.48.0) |
| `ssl` | covered | `ssl` + `SSLContext` namespaces (v0.48.0) |
| `select` | out | Low-level — `selectors` is preferred |
| `selectors` | out | Low-level multiplexing |
| `signal` | covered | `signal` namespace (v0.48.0) |

### Internet Data Handling

| Module | Status | Sketch |
|---|---|---|
| `email` | covered | `email` / `EmailMessage` / `EmailUtils` / `EmailPolicy` namespaces (v0.46.0) |
| `json` | covered | `json` namespace (shipped in v0.25.0) |
| `mailbox` | out | Niche legacy |
| `mimetypes` | covered | `mimetypes` + `MimeTypes` (shipped in v0.15.0) |
| `base64` | covered | Methods on `Bytes` and `Str` (shipped in v0.13.0) |
| `binascii` | covered | `binascii` namespace (shipped in v0.14.0) |
| `quopri` | out | Niche legacy encoding |

### Structured Markup Processing Tools

| Module | Status | Sketch |
|---|---|---|
| `html` | covered | `html` + `HTMLParser` + `Entities` namespaces (v0.46.0) |
| `xml` | covered | `xml` + `ET` + `Element` + `ElementTree` namespaces, ElementTree-only (v0.46.0) |
| `xmlrpc` | out | Legacy protocol |
| `pyexpat` | out | Internal; covered by `xml` if ever |

### Internet Protocols and Support

| Module | Status | Sketch |
|---|---|---|
| `webbrowser` | covered | `webbrowser` + `Browser` (shipped in v0.16.0) |
| `wsgiref` | out | Reference impl |
| `urllib` | covered | `urllib` + `Request` + `Response` + `ParseResult` + `SplitResult` (shipped in this PR) |
| `http` | covered | `http` + `HTTPConnection` + `HTTPSConnection` + `HTTPResponse` + `SimpleCookie` + `Morsel` (shipped in this PR) |
| `ftplib` | out | Legacy protocol |
| `poplib` | out | Legacy protocol |
| `imaplib` | out | Legacy protocol |
| `smtplib` | covered | `smtplib` + `SMTP` + `SMTP_SSL` + `LMTP` (shipped in this PR) |
| `uuid` | covered | `uuid` + `UUID` (shipped in v0.24.0) |
| `socketserver` | out | Pairs with `socket` if ever |
| `ipaddress` | covered | `ipaddress` + `IPv4Address` + `IPv6Address` + `IPv4Network` + `IPv6Network` + `IPv4Interface` + `IPv6Interface` (shipped in this PR) |

### Multimedia Services

| Module | Status | Sketch |
|---|---|---|
| `wave` | out | Niche audio format |
| `colorsys` | out | Tiny niche helper |

### Internationalization

| Module | Status | Sketch |
|---|---|---|
| `gettext` | out | Niche |
| `locale` | covered | `locale` namespace (shipped in this PR) |

### Program Frameworks

| Module | Status | Sketch |
|---|---|---|
| `turtle` | out | Educational graphics |
| `turtledemo` | out | Pairs with `turtle` |
| `cmd` | out | REPL framework |
| `shlex` | covered | `shlex` + `Shlex` (shipped in v0.23.0) |

### Graphical User Interfaces

| Module | Status | Sketch |
|---|---|---|
| `tkinter` | out | GUI toolkit — out of scope |

### Development Tools

| Module | Status | Sketch |
|---|---|---|
| `typing` | out | POOP is dynamically typed in the Smalltalk tradition |
| `annotationlib` | out | Pairs with `typing` |
| `pydoc` | out | POOP has no docstring tooling |
| `pydoc_data` | out | Pairs with `pydoc` |
| `doctest` | out | Depends on `repr` (forbidden) |
| `unittest` | covered | `unittest` / `TestCase` / `TestSuite` / `TestRunner` / `TestResult` namespaces (v0.47.0) |
| `ensurepip` | out | Packaging |
| `venv` | out | Packaging |
| `zipapp` | out | Packaging |
| `idlelib` | out | IDE |

### Debugging and Profiling

| Module | Status | Sketch |
|---|---|---|
| `bdb` | out | Debugger framework — depends on introspection |
| `faulthandler` | out | C-level crash dumps |
| `pdb` | out | Depends on introspection |
| `profile` / `cProfile` / `pstats` | covered | `cProfile` / `Profile` / `pstats` / `Stats` / `SortKey` namespaces (v0.47.0) |
| `timeit` | covered | `timeit` / `Timer` namespaces (v0.47.0) |
| `trace` | out | Depends on introspection |
| `tracemalloc` | out | Depends on introspection |

### Python Runtime Services

| Module | Status | Sketch |
|---|---|---|
| `sys` | covered | `sys` / `args` / `stdout` / `stderr` / `stdin` namespaces (v0.45.0) |
| `sysconfig` | out | Build-time metadata |
| `builtins` | out | POOP *replaces* this |
| `warnings` | out | POOP doesn't have a warning concept |
| `dataclasses` | out | POOP classes don't use decorators |
| `contextlib` | covered | Reachable via `With` |
| `abc` | out | All POOP classes can be subclassed |
| `atexit` | covered | `atexit` namespace (v0.45.0) |
| `traceback` | out | Depends on introspection |
| `gc` | covered | `gc` namespace, control surface only (v0.45.0) |
| `inspect` | out | Forbidden — POOP rejects introspection |
| `site` | out | Site-packages plumbing |

### Custom Python Interpreters

| Module | Status | Sketch |
|---|---|---|
| `code` | out | Embeddable REPL |
| `codeop` | out | Pairs with `code` |

### Importing Modules

| Module | Status | Sketch |
|---|---|---|
| `importlib` | out | POOP forbids imports |
| `zipimport` | out | Pairs with `importlib` |
| `pkgutil` | out | Pairs with `importlib` |
| `modulefinder` | out | Pairs with `importlib` |
| `runpy` | out | Pairs with `importlib` |

### Python Language Services

| Module | Status | Sketch |
|---|---|---|
| `ast` | out | Used internally by POOP itself; not surfaced |
| `symtable` | out | Compiler internal |
| `token` / `tokenize` | out | Lexer internal |
| `keyword` | out | Lexer internal |
| `tabnanny` | out | Linter |
| `pyclbr` | out | Class browser |
| `py_compile` / `compileall` | out | Build helpers |
| `dis` | out | Bytecode disassembler |
| `pickletools` | out | Pairs with `pickle` |
| `opcode` | out | Internal |

### Unix-Specific Services

| Module | Status | Sketch |
|---|---|---|
| `posix` | out | Low-level — covered via `os` if at all |
| `pwd` | covered | `pwd` + `Passwd` (shipped in this PR) |
| `grp` | covered | `grp` + `Group` (shipped in this PR) |
| `termios` / `tty` / `pty` | out | Low-level TTY |
| `fcntl` | out | Low-level file control |
| `resource` | covered | `resource` + `RUsage` (shipped in this PR) |
| `syslog` | out | Niche logging |

### Windows-Specific Services

| Module | Status | Sketch |
|---|---|---|
| `msvcrt` | out | Low-level |
| `winreg` | out | Niche registry |
| `winsound` | out | Niche audio |
| `nt` | out | Internal counterpart to `posix` |

### Superseded / Internal / Easter Eggs

| Module | Status | Sketch |
|---|---|---|
| `optparse` | out | Superseded by `argparse`; both out of scope anyway |
| `getopt` | out | Superseded by `argparse` |
| `sre_compile` / `sre_constants` / `sre_parse` | out | `re` internals |
| `encodings` | out | Codec implementations — surfaced via `Str`/`Bytes` |
| `antigravity` | out | Easter egg |
| `this` | out | Easter egg |

This is **scoping work**, not implementation work — the audit should
produce a per-module decision and either a follow-up proposal or a
"stays out" entry. Implementation happens proposal-by-proposal.

## Future work

Items deferred from shipped proposals that need their own follow-up
once a prerequisite exists.

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

### Complex math (`cmath`) — from the `math` proposal (v0.6.0)

The `Math` namespace deliberately omits `cmath` because it requires
a `Complex` POOP type with a fully-fleshed message API. POOP has a
`Complex` wrapper today (`poop/types/complex.py`) used by literal
transforms and arithmetic, but it does not yet expose the
transcendental surface (`cmath.sqrt`, `cmath.exp`, `cmath.sin`,
`cmath.phase`, `cmath.polar`, `cmath.rect`, `cmath.isclose`,
`cmath.isfinite`/`isinf`/`isnan`, and the constants
`cmath.pi`/`e`/`tau`/`inf`/`nan`/`infj`/`nanj`).

When written, the `cmath` proposal should mirror the shape of the
`math` namespace exactly — a `CMath` namespace-only injection (or
fold the operations onto the existing `Complex` POOP type, TBD),
with the same constant-case rule (lowercase, mirroring source).
Cross-cutting decisions to make first:

- Are `Complex` arithmetic predicates (`.isfinite()` / `.isinf()` /
  `.isnan()`) Float-typed on the real and imaginary parts, or
  defined on the whole `Complex`? Python defines the latter on
  `cmath.*`.
- Should `cmath` and `math` share predicates that take Complex
  (returning Boolean) or duplicate them per type, like Python does?

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
POOP does not have (see `warnings` in the audit table: "out").
v0.11.0 ships `getpass.getpass` and `getpass.getuser` but does not
expose `GetPassWarning`; the underlying CPython call still emits the
warning to stderr, POOP user code just cannot catch or filter it.

A proper exposure would require either (a) a POOP `Warning`/`Stream`
story to mirror `warnings.filterwarnings` and friends, or (b)
upgrading the warning to a raised `Error` and letting POOP's `Try`
catch it — diverging from Python's actual behavior. Deferred until
a concrete user need surfaces.

