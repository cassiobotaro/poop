# Proposals

## Expose `math` functions as POOP messages

Python's `math` module is currently unreachable from POOP code because
imports are forbidden. There is no idiomatic way to compute `sqrt`,
`sin`, `log`, etc. in POOP source today.

Smalltalk handles this with **messages on numbers** — `2 sqrt`, `1.0 sin`,
`100 ln`, `30 degreesToRadians sin`. There is no `Math` global; the
behavior lives on `Number` (and concretely on `Float`). POOP should
adopt the same model where it fits, with a pragmatic fallback for
multi-argument helpers and constants.

**Proposal — hybrid model:**

1. **Unary functions become methods on `Int` / `Float`.** The receiver
   is obvious and the message reads naturally:
   - `(2.0).sqrt()`, `(2.0).sin()`, `(2.0).cos()`, `(2.0).tan()`
   - `(2.0).asin()`, `(2.0).acos()`, `(2.0).atan()`
   - `(2.0).sinh()`, `(2.0).cosh()`, `(2.0).tanh()`
   - `(2.0).asinh()`, `(2.0).acosh()`, `(2.0).atanh()`
   - `(2.0).exp()`, `(2.0).log()`, `(2.0).log2()`, `(2.0).log10()`,
     `(2.0).log1p()`
   - `(2.0).floor()`, `(2.0).ceil()`, `(2.0).trunc()`
   - `(0.5).degrees()`, `(0.5).radians()` (Python's `math.degrees` /
     `math.radians`)
   - `(0.5).erf()`, `(0.5).erfc()`, `(0.5).gamma()`, `(0.5).lgamma()`
   - `(n).factorial()` (Int only)
   - `(a).is_finite()`, `(a).is_infinite()`, `(a).is_nan()` (already
     fits the `is_xxx() -> Boolean` pattern)
2. **Binary / multi-argument helpers become a `Math` namespace-only
   object** (same family as `Try` / `With` / `Path`):
   - `Math.atan2(y, x)`, `Math.hypot(x, y, ...)`, `Math.copysign(x, y)`,
     `Math.gcd(a, b)`, `Math.lcm(a, b)`, `Math.dist(p, q)`,
     `Math.fmod(a, b)`, `Math.remainder(a, b)`, `Math.comb(n, k)`,
     `Math.perm(n, k)`, `Math.fsum(iterable)`, `Math.prod(iterable)`,
     `Math.isclose(a, b, ...)`
3. **Constants live on `Math`:** `Math.pi`, `Math.e`, `Math.tau`,
   `Math.inf`, `Math.nan`. Methods returning `Float`.

`MathTransformer` is **namespace-only** (no AST rewrite); it injects
`Math` into `DEFAULT_NAMESPACE` like `Try` / `With` / `Path`.

**Type discipline:** every signature exposed by this proposal — the
new methods on `Int` / `Float`, and every method, attribute, and
constant on `Math` — takes and returns POOP types (`Int`, `Float`,
`Boolean`, `List`, ...). No Python primitives leak across the
boundary, even for convenience or to keep tests shorter. This applies
both to public-facing annotations and to the runtime values returned.

**Smalltalk reference.** The mapping below documents where each
Python operation comes from in Pharo/Squeak and where POOP departs
from Smalltalk on purpose. "(no native)" means the dialect doesn't
ship the operation in base; the idiom in the Notes column is what a
Smalltalker would write.

*Unary, dispatched on `Int` / `Float`:*

| Python | Smalltalk | Notes |
|---|---|---|
| `math.sqrt(x)` | `x sqrt` | direct |
| `math.sin(x)` / `cos` / `tan` | `x sin` / `cos` / `tan` | direct |
| `math.asin(x)` / `acos` / `atan` | `x arcSin` / `arcCos` / `arcTan` | POOP keeps Python's `asin` etc. for discoverability |
| `math.sinh(x)` / `cosh` / `tanh` | `x sinh` / `cosh` / `tanh` | Pharo only; older dialects need an extension |
| `math.asinh(x)` / `acosh` / `atanh` | `x arcSinh` / `arcCosh` / `arcTanh` | same shift as `arcSin` family |
| `math.exp(x)` | `x exp` | direct |
| `math.log(x)` | `x ln` | **mismatch**: in Smalltalk `log` = log10, `ln` = natural log; POOP follows Python (`.log()` = natural) |
| `math.log10(x)` | `x log` | (see above) |
| `math.log2(x)` | `x log: 2` | Smalltalk uses keyword `log:` for arbitrary base |
| `math.log1p(x)` | (no native) | `(x + 1) ln` |
| `math.floor(x)` | `x floor` | direct |
| `math.ceil(x)` | `x ceiling` | POOP keeps Python's shorter `ceil` |
| `math.trunc(x)` | `x truncated` | POOP keeps Python's `trunc` |
| `math.degrees(x)` | `x radiansToDegrees` | **direction inverted**: Python `degrees(x)` is radians→degrees; Smalltalk reads the destination |
| `math.radians(x)` | `x degreesToRadians` | (same gotcha) |
| `math.erf(x)` / `erfc` / `gamma` / `lgamma` | (no native) | not in base Pharo; community packages add them |
| `math.factorial(n)` | `n factorial` | direct, integer only in both |
| `math.isfinite(x)` | `x isFinite` | direct |
| `math.isinf(x)` | `x isInfinite` | POOP keeps Smalltalk's clearer `is_infinite()` |
| `math.isnan(x)` | `x isNaN` | direct |

*Multi-argument, dispatched on `Math`:*

| Python | Smalltalk | Notes |
|---|---|---|
| `math.atan2(y, x)` | `y arcTan: x` | Smalltalk uses keyword msg with `y` as receiver; `Math.atan2(y, x)` reads more clearly than `(y).atan2(x)` |
| `math.hypot(x, y, ...)` | `x hypot: y` | Pharo only covers 2D — POOP keeps Python's N-dim varargs |
| `math.copysign(x, y)` | (no native) | idiom: `y sign * x abs` |
| `math.gcd(a, b, ...)` | `a gcd: b` | Smalltalk is binary-only; POOP keeps Python's varargs |
| `math.lcm(a, b, ...)` | `a lcm: b` | same as `gcd` |
| `math.dist(p, q)` | `(3 @ 4) dist: (0 @ 0)` | Smalltalk has it on `Point` (2D); for N-dim, loop |
| `math.fmod(a, b)` | (no exact) | Smalltalk's `\\` is floor-mod; `fmod` is trunc-mod — different on negatives |
| `math.remainder(a, b)` | (no native) | IEEE 754 remainder; manual implementation |
| `math.comb(n, k)` / `perm(n, k)` | (no native) | extension package in Pharo |
| `math.fsum(iter)` | `iter sum` | Pharo's `Collection>>#sum` exists; `fsum` adds Kahan summation |
| `math.prod(iter)` | (no native) | idiom: `iter inject: 1 into: [:a :b ǀ a * b]` |
| `math.isclose(a, b)` | `a closeTo: b` | Pharo has it with a default tolerance |

*Constants on `Math`:*

| Python | Smalltalk | Notes |
|---|---|---|
| `math.pi` | `Float pi` | class-side method on `Float` |
| `math.e` | `Float e` | class-side |
| `math.tau` | (no native) | not standard in Smalltalk; would be `Float pi * 2` |
| `math.inf` | `Float infinity` | class-side; POOP keeps Python's shorter `inf` |
| `math.nan` | `Float nan` | class-side |

A pure-Smalltalk port would put the constants on `Float` class-side
(`Float.pi`) instead of `Math.pi`, and dispatch all binary ops
through keyword messages on the receiver. POOP chooses `Math` for
those cases for readability with Python eyes; the table makes the
divergence explicit so future readers can see the trade.

**Out of scope (for v1):**

- The bit/integer-specific helpers (`bit_length`, `bit_count`) already
  live on `Int` and stay there.
- `math.frexp` / `math.modf` / `math.ldexp` — niche; defer until
  someone asks.
- Complex math (`cmath`) — orthogonal, would need its own proposal.

**Open question:** should `Float`'s `is_finite()` / `is_infinite()` /
`is_nan()` be class-level on `Math` too (mirroring `math.isfinite(x)`)?
Argument for both: receiver-method form reads naturally; class-level
mirror keeps API discoverable for Python users searching for
`isfinite`. Argument against: duplication for no semantic gain.

## Audit the rest of the Python stdlib for POOP equivalents

Following the `math` proposal above, the same question applies to
every other commonly-used Python module: imports are forbidden in
POOP, so anything in the stdlib is currently unreachable from POOP
code. Each module needs a decision about whether — and how — to
surface it inside POOP, without breaking the message-passing model.

Three Smalltalk patterns are already in use and should guide the
decision case-by-case:

- **Message on the value** — when the operation belongs to a single
  receiver (`'abc'.is_digit()`, `(2.0).sqrt()`, `coll.sort()`).
- **Class-with-class-methods (`Math`-style namespace global)** — when
  the operation parses, creates, or combines values (`Random new`,
  `Date today`, `NeoJSONReader fromString:`, `Math.atan2`). In POOP
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
| `string` | audit | Constants (`ascii_letters`, …) on the `Str` class side |
| `re` | audit | Message on `Str`: `'abc'.matches('a.*')`, `'abc'.regex_matches('\\d+')` |
| `difflib` | audit | `Str.diff(other)` — likely own proposal |
| `textwrap` | audit | Messages on `Str`: `.wrap(width)`, `.indent(prefix)`, `.dedent()` |
| `unicodedata` | audit | Messages on `Str` (`.normalize()`) or `Unicode` namespace |
| `stringprep` | out | Internal IDNA helper |
| `readline` | out | REPL infrastructure — POOP doesn't expose a REPL |
| `rlcompleter` | out | REPL infrastructure |

### Binary Data Services

| Module | Status | Sketch |
|---|---|---|
| `struct` | audit | `Bytes.unpack(fmt)` / `Struct.pack(fmt, …)` — own proposal |
| `codecs` | audit | Mostly covered by `Str.encode` / `Bytes.decode`; rarer codecs need a call |

### Data Types

| Module | Status | Sketch |
|---|---|---|
| `datetime` | audit | Class factories — `DateTime.now()`, `Date.today()` |
| `zoneinfo` | audit | Pairs with `datetime` |
| `calendar` | audit | `Calendar` namespace |
| `collections` | covered | `OrderedDict` / `Counter` / `deque` redundant — POOP collections carry the methods |
| `heapq` | audit | Methods on `List` (`.heap_push`, `.heap_pop`) or `Heap` type |
| `bisect` | audit | `List.bisect(x)` / `.insert_sorted(x)` |
| `array` | audit | Typed dense array vs POOP `List` — defer unless needed |
| `weakref` | audit | Low priority |
| `types` | out | Introspection — forbidden in POOP |
| `copy` | audit | `obj.copy()` / `obj.deep_copy()` on `Object` |
| `pprint` | audit | Pairs with eventual print story |
| `reprlib` | out | POOP forbids `repr` |
| `enum` | audit | POOP classes already support class-side singletons |
| `graphlib` | audit | `Graph` type or namespace |

### Numeric and Mathematical Modules

| Module | Status | Sketch |
|---|---|---|
| `numbers` | out | ABC hierarchy — POOP has its own type tree |
| `math` | proposed | See proposal above |
| `cmath` | audit | Deferred by the `math` proposal; needs Complex story |
| `decimal` | audit | `Decimal` POOP type with full message API |
| `fractions` | audit | `Fraction` POOP type |
| `random` | audit | `Random.new()`, `coll.at_random()` (Smalltalk-style) |
| `statistics` | audit | `coll.mean()` / `coll.median()` or `Statistics` namespace |

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
| `filecmp` | audit | `Path.diff(other)`? |
| `tempfile` | audit | `Path.temp_file()` / `Path.temp_dir()` |
| `glob` | audit | `Path.glob(pattern)` (may already exist) |
| `fnmatch` | audit | `Str.matches_glob(pattern)` |
| `linecache` | out | Internal traceback helper |
| `shutil` | audit | High-level ops as messages on `Path` |

### Data Persistence

| Module | Status | Sketch |
|---|---|---|
| `pickle` | audit | `Path.dump(obj)` / `Path.load()` — security caveats |
| `copyreg` | out | Internal hook for `pickle` |
| `shelve` | out | Depends on `dbm` |
| `marshal` | out | CPython internal |
| `dbm` | out | Niche; prefer `sqlite3` |
| `sqlite3` | audit | `Database.open(path)` class factory — own proposal |

### Data Compression and Archiving

| Module | Status | Sketch |
|---|---|---|
| `zlib` | audit | `Bytes.compress()` / `Bytes.decompress()` |
| `gzip` | audit | `Path.gunzip()` / `Path.gzip()` |
| `bz2` | audit | Same shape as `gzip` |
| `lzma` | audit | Same shape as `gzip` |
| `zipfile` | audit | `Zip.open(path)` namespace |
| `tarfile` | audit | `Tar.open(path)` namespace |
| `compression` | audit | New 3.14 wrapper namespace — track upstream |

### File Formats

| Module | Status | Sketch |
|---|---|---|
| `csv` | audit | `Csv.parse(s)` / `Path.read_csv()` — own proposal |
| `configparser` | audit | `Ini.parse(s)` namespace |
| `tomllib` | audit | `Toml.parse(s)` — read-only, simple |
| `netrc` | out | Niche legacy format |
| `plistlib` | out | macOS-specific niche |

### Cryptographic Services

| Module | Status | Sketch |
|---|---|---|
| `hashlib` | audit | `Str.sha256()` / `Bytes.sha256()` or `Hash` namespace |
| `hmac` | audit | Pairs with `hashlib` |
| `secrets` | audit | Pairs with `random` |

### Generic Operating System Services

| Module | Status | Sketch |
|---|---|---|
| `os` | audit | Split: `System`, `Platform`, `Env`, `Process` |
| `io` | audit | Streams largely via `Path`; `StringIO`/`BytesIO` deferred |
| `time` | audit | Pairs with `datetime` |
| `logging` | audit | `Logger` namespace if a logging story emerges |
| `argparse` | out | POOP programs don't expose a CLI surface (yet) |
| `getpass` | audit | `Stdin.password()` if a stdin story emerges |
| `curses` | out | Terminal UI — niche |
| `platform` | audit | `Platform.name`, `Platform.version` |
| `errno` | audit | Constants on `Error` class? |
| `ctypes` | out | FFI — clashes with introspection rules |
| `mmap` | out | Low-level; defer until needed |

### Concurrent Execution

| Module | Status | Sketch |
|---|---|---|
| `threading` | audit | Smalltalk uses `Process` — POOP equivalent TBD |
| `multiprocessing` | audit | Pairs with `threading` |
| `concurrent` | audit | Futures — `Block.fork()` returning a `Future`? |
| `subprocess` | audit | `Process.run(cmd)` class factory |
| `sched` | out | Niche scheduler |
| `queue` | audit | `Queue` POOP type |
| `contextvars` | out | Implementation detail |

### Networking and Interprocess Communication

| Module | Status | Sketch |
|---|---|---|
| `asyncio` | audit | Huge surface — own proposal |
| `socket` | audit | `Socket.open(addr)` class factory |
| `ssl` | audit | Pairs with `socket` |
| `select` | out | Low-level — `selectors` is preferred |
| `selectors` | out | Low-level multiplexing |
| `signal` | audit | `System.on_signal(sig, block)` |

### Internet Data Handling

| Module | Status | Sketch |
|---|---|---|
| `email` | audit | Own proposal — `Email.parse(s)` |
| `json` | audit | `Json.parse(s)` / `Json.dumps(obj)` |
| `mailbox` | out | Niche legacy |
| `mimetypes` | audit | `Path.mime_type` message |
| `base64` | audit | `Bytes.to_base64()` / `Str.from_base64()` |
| `binascii` | audit | Pairs with `base64` |
| `quopri` | out | Niche legacy encoding |

### Structured Markup Processing Tools

| Module | Status | Sketch |
|---|---|---|
| `html` | audit | `Str.escape_html()` / `Str.unescape_html()` |
| `xml` | audit | Own proposal — `Xml.parse(s)` |
| `xmlrpc` | out | Legacy protocol |
| `pyexpat` | out | Internal; covered by `xml` if ever |

### Internet Protocols and Support

| Module | Status | Sketch |
|---|---|---|
| `webbrowser` | audit | `System.open_browser(url)` |
| `wsgiref` | out | Reference impl |
| `urllib` | audit | HTTP client — own proposal |
| `http` | audit | Pairs with `urllib` |
| `ftplib` | out | Legacy protocol |
| `poplib` | out | Legacy protocol |
| `imaplib` | out | Legacy protocol |
| `smtplib` | audit | `Smtp` namespace if a mail story emerges |
| `uuid` | audit | `Uuid.new()` class factory |
| `socketserver` | out | Pairs with `socket` if ever |
| `ipaddress` | audit | `IpAddress` POOP type |

### Multimedia Services

| Module | Status | Sketch |
|---|---|---|
| `wave` | out | Niche audio format |
| `colorsys` | out | Tiny niche helper |

### Internationalization

| Module | Status | Sketch |
|---|---|---|
| `gettext` | out | Niche |
| `locale` | audit | `Locale` namespace |

### Program Frameworks

| Module | Status | Sketch |
|---|---|---|
| `turtle` | out | Educational graphics |
| `turtledemo` | out | Pairs with `turtle` |
| `cmd` | out | REPL framework |
| `shlex` | audit | `Str.shell_split()` |

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
| `unittest` | audit | POOP testing story TBD |
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
| `profile` / `cProfile` / `pstats` | audit | `Block.profile()`? |
| `timeit` | audit | `Block.benchmark()` |
| `trace` | out | Depends on introspection |
| `tracemalloc` | out | Depends on introspection |

### Python Runtime Services

| Module | Status | Sketch |
|---|---|---|
| `sys` | audit | Split: `System`, `Stdout`/`Stderr`, `Args` |
| `sysconfig` | out | Build-time metadata |
| `builtins` | out | POOP *replaces* this |
| `warnings` | out | POOP doesn't have a warning concept |
| `dataclasses` | out | POOP classes don't use decorators |
| `contextlib` | covered | Reachable via `With` |
| `abc` | out | All POOP classes can be subclassed |
| `atexit` | audit | `System.at_exit(block)` |
| `traceback` | out | Depends on introspection |
| `gc` | audit | `System.gc()` |
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
| `pwd` | audit | `System.user`? |
| `grp` | audit | Pairs with `pwd` |
| `termios` / `tty` / `pty` | out | Low-level TTY |
| `fcntl` | out | Low-level file control |
| `resource` | audit | `System.resource_limit(…)` |
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
