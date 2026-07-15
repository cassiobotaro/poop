# Smalltalk Infections

Infections come in two kinds:
- **Validators** (`poop/validators/`) — reject code incompatible with POOP; follow the `Validator` + `ast.NodeVisitor` pattern.
- **Transformers** (`poop/transformers/`) — rewrite the AST before execution to replace Python constructs with POOP equivalents; follow the `Transformer` + `ast.NodeTransformer` pattern.

Pipeline: `parse → validate → transform → execute(namespace)`

## Principles

- **Everything is an object** and every operation is **message passing**.
- There are no control flow structures — conditionals and iterations are messages sent to objects.
- There are no free functions — all behavior lives in class methods.
- **Message aesthetics**: the central criterion of an infection is not "does it exist in Smalltalk?" but rather "does it look like an object receiving a message?". Operators (`-x`, `not x`, `~x`) and free functions (`len(x)`, `abs(x)`) have a procedural look even when they call methods internally — they must be replaced by `x.negated()`, `x.not_()`, `x.bit_invert()`, `x.len()`, `x.abs()`. POOP code must look like a conversation between objects, not a sequence of operations.
- **Method names in Python, not Smalltalk**: all methods follow the corresponding Python name — builtins, dunders and collection API. `map` not `collect`, `filter` not `select`, `filter_false` not `reject`, `find` not `detect`. Smalltalk names are not implemented. **Exception**: iteration uses `do` (from Smalltalk `do:`) instead of `for_each` — `for` is a Python keyword and `for_each` is a Java/JS idiom with no Python equivalent; `do` is the canonical Smalltalk message for iteration and reads naturally as a message to an object. It returns `none`, like a `for` loop. Folds use `reduce(init, block)` (Smalltalk's `inject:into:`); it is named `reduce` after `functools.reduce`, which is the Python name for the same operation.
- **Activate validator only when the substitute exists**: blocking without offering an alternative only breaks code without teaching anything. Validators without an implemented substitute live in `proposals.md` until the alternative is ready. *Exception*: **definitive bans** — constructs with no possible substitute inside POOP's model (`exec`/`eval`/`compile`, `exit`/`quit`, `breakpoint`, `globals`/`locals`/`vars`, `open`) are activated without a substitute and tracked under `proposals.md` § "Stay banned (no proposal)".
- **Representation**: all POOP types implement `__str__` (and `__repr__` delegates to it). `Object.print` calls `str(obj)` internally — every printed message goes through the type's own representation.
- **`__slots__` on all POOP types**: instance variables are declared in the class definition and fixed — never added dynamically to instances. Runtime *method* extension continues to work normally. Subclasses that need new instance variables can declare their own `__slots__` or omit them.
- **Every literal is transformed**: every literal in Python source (`1`, `3.14`, `"hello"`, `True`, `False`, `None`, `[1, 2]`, `(1, 2)`, `{1, 2}`, `{k: v}`, `b"..."`, `1+2j`) is rewritten by a Transformer into its POOP equivalent before execution — no naked Python primitive ever reaches runtime.
- **Every basic type has a POOP equivalent**: `int` → `Int`, `float` → `Float`, `str` → `Str`, `bool` → `Boolean`, `NoneType` → `NoneClass`, `list` → `List`, `tuple` → `Tuple`, `set` → `Set`, `frozenset` → `FrozenSet`, `dict` → `Dict`, `bytes` → `Bytes`, `bytearray` → `ByteArray`, `memoryview` → `MemoryView`, `complex` → `Complex`. Python native types must not leak into POOP code.
- **All POOP methods return POOP types**: every method on every POOP type must return a POOP object — never a raw Python `int`, `bool`, `str`, `list`, etc. Returning a native type is a bug. *Exception*: Python protocol dunders (`__bool__`, `__hash__`, `__len__`, `__str__`, `__int__`, `__float__`, `__contains__`, `__repr__`) must return native types because Python itself requires it for `if`, `dict`, `len()`, `str()`, etc. to work. The rule applies to all explicitly named POOP methods (`len()`, `hash()`, `not_()`, `includes()`, `tobytes()`, etc.).
- **Mutators named after Python void-returning methods return `none`**: methods that mirror Python counterparts returning `None` (e.g., `list.append`, `set.add`, `dict.update`, `bytearray.reverse`) must return POOP `none`, not `self`. This preserves the Python mirror contract — `result = lst.append(x)` leaves `result` as `none`, matching what a Python programmer expects. POOP-specific methods with no Python equivalent (e.g., `List.add`, `Dict.at_put`, `ByteArray.at_put`) may still return `self` for chaining.
- **`True`, `False`, and `None` are singletons**: `true`, `false`, and `none` are unique objects — there is exactly one instance of each. All comparisons and identity checks rely on this guarantee.
- **Constructor builtins are intercepted, not banned**: `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` etc. are class constructors — they ARE object instantiation and fit the OO model. Each transformer intercepts the bare call and rewrites it to return the POOP type via a `_poop_X_from(...)` factory.
- **Dunders exposed as regular methods**: every relevant dunder on a POOP type gets an alias with the Python name without underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__hash__` → `hash()`, etc. Do not translate to Smalltalk names.
- **Namespace hygiene — POOP types pass as Python builtins**: every wrapper class (`Int`, `List`, `Object`, …) is bound under a mangled `_poop_*` name and unreachable from user code (enforced by `no_poop_prefix`). The bare Python builtin (`int`, `list`, `object`, …) is rewritten at parse time to the corresponding mangled name. Each wrapper additionally patches `__module__ = "builtins"` and `__name__ = "<lowercase>"`, so `repr(Int)` reads `<class 'int'>` and `Int(5).class_name()` returns `Str("int")` — POOP builtins answer to the same names Python builtins do. True entry points without an AST rewrite or method equivalent fall in two camps: **POOP-specific constructs** (`Try`, `With`, `Path`) keep PascalCase, and **Python stdlib module mirrors** (`math`, `random`, …) keep lowercase to match the source module names. A module that also exposes a class (e.g., `random` ⊃ `Random`) binds both — the lowercase name for module-level entry, the PascalCase name for the class constructor.

## Project conventions

Rules every namespace wrapper in `poop/types/` must follow. Recorded here so reviewers and future PRs apply the same yardstick.

### Mirror Python's attribute vs method shape

If CPython exposes a name as an **attribute** (`sys.argv`, `time.tzname`, `Element.tag`, `ctx.verify_mode`), POOP exposes it as an attribute too — `ClassVar` for constants, `@property` for computed-on-read values. If CPython exposes it as a **method** (`logger.info(msg)`, `subprocess.run(args)`), POOP exposes it as a method. User code reads `sys.argv`, not `sys.argv`.

Forcing attribute-shaped surfaces into zero-arg methods (`sys.argv`, `time.tzname`) breaks Python intuition and gains nothing for message-passing — `obj.attr` is already a message in Python's data model.

### Assignment, not setter methods

When a Python attribute can be mutated (`logger.propagate = True`, `ctx.verify_mode = ssl.CERT_REQUIRED`), POOP uses normal Python assignment — implemented via `@X.setter`. No `.set_X(value)` method convention. The Python idiom is `obj.attr = value`; POOP follows it.

### Default kwarg policy

POOP method defaults mirror CPython exactly. If CPython writes `subprocess.run(args, *, check=False, capture_output=False)`, POOP writes `check=false`, not `check=none`. Defaulting to `none` silently merges "user passed `false`" with "user did not pass" — for bool flags this is harmless, for tri-state semantics it breaks. Mirror CPython and let the underlying call distinguish.

The only sanctioned `none`-default is when CPython itself uses `None` as the sentinel (e.g., `socket.gethostbyname(name, default=None)`).

Parameter names also mirror CPython where there is no banned-builtin or POOP-specific clarification at stake. Documented divergences:

- POOP renames params that shadow banned builtins (e.g., `grp.getgrgid` takes `gid` instead of CPython's `id`).
- File I/O entry points take `Path` instead of file-object / file-descriptor (POOP has no file-object abstraction).
- CPython entry points that take `*args, **kwargs` (e.g., `textwrap.wrap`, `logging.basicConfig`, `pprint.pp`) expose their kwargs explicitly in POOP to preserve type information.

### Platform-specific constants

Constants that CPython exposes only on some platforms (`socket.AF_UNIX`, `signal.SIGUSR1`, `resource.RLIMIT_NPROC`) bind to POOP `none` on platforms that lack them — never raise on attribute access, never omit the name entirely. This way user code is portable and falsy-checks (`signal.SIGUSR1.is_none()`) work uniformly.

### Error class exposure

Every exception class that CPython raises through the wrapped surface and that a POOP user might reasonably pass to `Try.except_(...)` is exposed on the wrapping namespace. `json.JSONDecodeError`, `subprocess.CalledProcessError`, `ssl.SSLError`, `urllib.URLError` — all surface. Internal-only error classes (CPython's `_ssl.SSLError` aliases, `_socket.error` aliases) stay hidden.

### Pull deferred surface only when a caller asks

POOP's stdlib mirrors cover the daily-use surface of each wrapped module; long-tail items (rare-call helpers, debug-only flags, niche per-platform constants) stay out until a real caller surfaces. Surfacing them upfront just inflates the API and creates churn — wait for a concrete use case, then wrap with the same POOP-type-discipline contract as the rest of the namespace. New requests open issues against the project; they should not gate the 1.0 release.

## Permanent divergences from CPython

Surfaces POOP intentionally does not mirror — not deferred, not a backlog item, decided out. User code that wants any of these calls into raw CPython (POOP doesn't sandbox you out of `import`-on-the-Python-side; it just doesn't bless these via the POOP namespace).

### No file-descriptor I/O

POOP file I/O routes through `Path`. The CPython fd-integer ABI (`os.open` / `os.close` / `os.read` / `os.write` / `os.dup` / `os.dup2` / `os.pipe` / `os.fdopen` / `os.closerange` / `os.lseek` / `os.fsync` / `os.fdatasync` / `os.ftruncate` / `os.fchmod` / `os.fchown` / `os.fstat` / `os.openpty` / `os.eventfd*` / `os.memfd_create` / `os.pidfd_open` / `signal.set_wakeup_fd`, etc.) stays out. Same for the `*at`-suffixed dir-fd variants (`os.openat`, `os.linkat`, `os.unlinkat`, `os.symlinkat`, `os.fchmodat`, `os.fchownat`, `os.fstatat`, …). Use `Path` (`read_text` / `write_text` / `read_bytes` / `write_bytes`).

### No process replacement / forking

`Subprocess` and `Multiprocessing` cover the daily-use surface. The lower-level `os.exec*` family (`execv` / `execve` / `execvp` / `execvpe` / `execl` / `execle` / `execlp` / `execlpe`), `os.fork` / `os.forkpty`, `os.posix_spawn` / `os.posix_spawnp`, `os.wait*` (`waitpid` / `wait3` / `wait4` / `waitstatus_to_exitcode`), `os.spawn*` (`spawnv*` / `spawnl*` / `spawnvp*` / `spawnlp*`), and `os.startfile` stay out. Same for scheduling (`os.sched_*`) and resource-priority knobs (`os.nice`, `os.getpriority`, `os.setpriority`).

### No frame-model / refcount / audit introspection

POOP intentionally hides CPython's frame model. `sys.getframe` / `sys._getframe` / `sys._current_frames`, `sys.getrefcount`, `sys.gettrace` / `sys.settrace` / `sys.setprofile`, `sys.audit` / `sys.addaudithook`, `sys.monitoring`, `sys.set_coroutine_origin_tracking_depth`, `sys.set_asyncgen_hooks`, `gc.get_referents` / `gc.get_referrers` / `gc.get_stats` / `gc.set_debug` all stay out. POOP debuggers/profilers are a non-goal — use CPython tools directly on the Python side if you need them.

### No `GetPassWarning`

`getpass.getpass` emits a `UserWarning` (CPython's `GetPassWarning`) to stderr when echo-suppression fails on the underlying TTY. POOP has no `warnings` model, so the warning is unobservable through the POOP namespace; user code cannot catch or filter it. Upgrading the warning to a raised POOP `Error` would diverge from CPython's actual behaviour — not worth the divergence.

### No `random.SystemRandom`

`random.SystemRandom` (cryptographic-quality randomness via `os.urandom`) stays out of the `random` namespace by design — POOP routes cryptographic draws through the `secrets` namespace, which already wraps the same underlying source. Splitting "use-as-stand-in-for-Random" vs. "I want crypto" by namespace makes the security intent visible at the call site.

### No `uuid.SafeUUID`

`uuid.UUID.is_safe` returns a `uuid.SafeUUID` enum value (`safe` / `unsafe` / `unknown`). POOP flattens this to a `Str` token on the wrapped `UUID`, sidestepping a one-shot enum exposure that nothing else in the namespace uses.

### No `datetime.MAXYEAR` / `datetime.MINYEAR`

CPython exposes `datetime.MAXYEAR` (`9999`) and `datetime.MINYEAR` (`1`) as module-level constants. POOP hides them behind `Date(year, month, day)`'s range-check semantics — passing an out-of-range year raises `ValueError` through the `Date` constructor, which is the same enforcement at a more natural call site. Surfacing the constants separately would just duplicate values already implicit in the type.

### No `os.chroot`

`os.chroot(path)` is a privileged-process operation that changes the calling process's root directory. POOP omits it: it has no clean reversible POOP idiom (a `Path` argument suggests symmetry with regular path ops, but `chroot` reshapes the *process's* filesystem view irrevocably), and the use case (jail/sandbox setup) is system-administration territory that POOP doesn't try to mirror.

### No `time.pthread_getcpuclockid`

Linux-only helper that maps a `pthread` thread ID to a per-thread CPU clock ID for `time.clock_gettime`. POOP exposes `CLOCK_THREAD_CPUTIME_ID` for the current thread's CPU clock, which covers the common case; cross-thread clock inspection via `pthread` IDs requires platform-conditional plumbing for a niche use case.

### No archive-format CPython internals

`zipfile.PyZipFile` (a CPython-bytecode-only ZIP variant), `zipfile.ZipExtFile` (the internal stream returned by `ZipFile.open()`), the `zipfile.struct*` format constants (`structCentralDir`, `structFileHeader`, etc.), the `tarfile` private error subclasses (`InvalidHeaderError`, `SubsequentHeaderError`, `TruncatedHeaderError`, `EOFHeaderError`, `EmptyHeaderError`, `LinkFallbackError`), and the `tarfile` encoding helpers (`itn`, `nti`, `stn`, `nts`, `calc_chksums`) stay out. They are CPython-internal — neither documented in the public API nor stable across releases — and would invite users to bind against private surface. The public `ZipFile` / `TarFile` / `GzipFile` wrappers cover the daily use case.

### No `codecs` registry / incremental protocol

The `codecs` namespace mirrors the daily-use encode/decode functions and the high-level `CodecInfo` lookup. The registry surface (`codecs.register`, `codecs.lookup`, `codecs.lookup_error`, `codecs.register_error`, `codecs.unregister`) and the incremental encoder/decoder protocol (`IncrementalEncoder`, `IncrementalDecoder`, `BufferedIncrementalEncoder`, `BufferedIncrementalDecoder`, `StreamReader`, `StreamWriter`, `StreamReaderWriter`, `StreamRecoder`, `EncodedFile`) plus the base `Codec` class stay out. They exist for writing new codec implementations, which is a process-wide Python-level customisation point with no clean POOP-type mapping — and the existing encoders cover everything POOP user code typically needs.

### No `logging.Manager` / `RootLogger` / `PlaceHolder`

`logging.Manager` and `logging.PlaceHolder` are internal classes the stdlib uses to construct the logger hierarchy; `RootLogger` is the singleton at the root of that hierarchy reachable as `logging.getLogger()`. POOP users access loggers through `Logging.getLogger(name)`, which already returns the root for the no-arg call. Surfacing these internal classes would invite users to bind against private structure that CPython doesn't promise to keep stable.

## Active infections

### No `if` — `poop/validators/no_if.py`

| AST node | Reason |
|---|---|
| `ast.If` | `if/elif/else` looks like control flow; use `x.if_true(block)` / `x.if_false(block)` |
| `ast.IfExp` | Ternary expression `x if cond else y` — same reason |

### No loops — `poop/validators/no_loops.py`

| AST node | Reason |
|---|---|
| `ast.For` | Loop looks procedural; use `col.do(block)`, `col.map(block)`, recursion |
| `ast.While` | Same; use `(lambda: cond).while_true(lambda: body)` |
| `ast.AsyncFor` | Async variant of `for`; use `await AsyncIO.do(aiter, block)` |

### No free functions — `poop/validators/no_free_functions.py`

| AST node | Context | Reason |
|---|---|---|
| `ast.FunctionDef` | outside class | Free function is not a message to any object |
| `ast.AsyncFunctionDef` | outside class | Async variant |

Functions inside classes (`class_depth > 0`) are allowed as methods.

### No `print` — `poop/validators/no_print.py`

| Call | Reason | Substitute |
|---|---|---|
| `print(...)` | Free function with procedural look | `obj.print()` |

### No `assert` — `poop/validators/no_assert.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Assert` | Statement — not a message to any object | `obj.assert_('message')` (any truthy receiver) |

### No `raise` — `poop/validators/no_raise.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Raise` | `raise` is a statement — not a message to any object | `ExcType.raise_('msg')` |

### No `try` — `poop/validators/no_try.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Try` | Control structure — procedural look | `Try(block).except_(ExcType, handler).run()` |
| `ast.TryStar` | `try/except*` variant (exception groups) | same |

### No `with` — `poop/validators/no_with.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.With` | Control structure — procedural look | `With(lambda: cm()).do(lambda resource: body)` |
| `ast.AsyncWith` | `async with` variant | `await AsyncWith(lambda: acm()).do(lambda resource: body)` |

### No `and`/`or` — `poop/validators/no_and_or.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.BoolOp` with `ast.And` | `x and y` looks like an operator | `x.and_(lambda: y)` |
| `ast.BoolOp` with `ast.Or` | `x or y` looks like an operator | `x.or_(lambda: y)` |

`and_` and `or_` receive a block so evaluation is lazy — the right-hand side is only evaluated if needed, preserving the short-circuit semantics of Python's `and`/`or`.

### `async def` / `await` — allowed inside class methods

POOP source can define `async def` methods and use `await` directly.
The validator pipeline forwards `ast.AsyncFunctionDef` and `ast.Await`
to compilation untouched; the coroutines are driven by `AsyncIO.run`
from the `asyncio` namespace.

The async-flavoured *control structures* remain banned by their
non-async validators: `ast.AsyncFor` by `no_loops` (use
`await AsyncIO.do(aiter, block)`), `ast.AsyncWith` by `no_with`
(use `await AsyncWith(lambda: acm()).do(block)`), and `async def`
*outside* a class by `no_free_functions`. Async generators are
forbidden indirectly — `yield` inside any function (sync or async)
is rejected by `no_yield`; consume external async iterables via
`AsyncIO.do` instead of authoring them in POOP.

### No `not` — `poop/validators/no_not.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.UnaryOp` with `ast.Not` | `not x` looks like an operator; it is not a message to `x` | `x.not_()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.UnaryOp` with `ast.USub` | operand is not `ast.Constant` | `-x` looks like an operator | `x.negated()` |

Negative literals (`-1`, `-3.14`) are allowed — only `-variable` and `-expression` are blocked.

### No unary plus — `poop/validators/no_unary_plus.py`

| AST node | Reason |
|---|---|
| `ast.UnaryOp` with `ast.UAdd` | `+x` is semantically a no-op and has no message-send equivalent — write the value directly |

### No bitwise invert — `poop/validators/no_invert.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.UnaryOp` with `ast.Invert` | `~x` looks like an operator | `x.bit_invert()` |

### No `is` / `is not` — `poop/validators/no_is.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Compare` with `ast.Is` | `is` looks like an operator | `x.is_none()` or `x.is_identical(other)` |
| `ast.Compare` with `ast.IsNot` | `is not` looks like an operator | `x.not_none()` or `x.not_identical(other)` |

### No `global`/`nonlocal` — `poop/validators/no_global.py`

| AST node | Reason |
|---|---|
| `ast.Global` | `global` breaks encapsulation — state lives in instances, not in global scope |
| `ast.Nonlocal` | `nonlocal` manipulates outer scope — use instance variables |

### No `yield` — `poop/validators/no_yield.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Yield` | generator has a procedural look for iteration | `col.do(block)`, `col.map(block)` |
| `ast.YieldFrom` | same | same |

### No walrus (`:=`) — `poop/validators/no_walrus.py`

| AST node | Reason |
|---|---|
| `ast.NamedExpr` | `:=` combines assignment and expression — use separate assignment |

### No `type` alias — `poop/validators/no_type_alias.py`

| Construct | Reason |
|---|---|
| `type X = int` | Creates an alias for a Python builtin type — incompatible with POOP runtime types |

### No `match/case` — `poop/validators/no_match.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.Match` | control structure with procedural look | polymorphism + `if_true(block)`/`if_false(block)` |

### No f-strings or t-strings — `poop/validators/no_fstring.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.JoinedStr` | `{...}` interpolation hides message sends and bypasses POOP `Str` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` |
| `ast.TemplateStr` | Python 3.14 t-strings share the `{...}` interpolation and yield a raw `Template`, bypassing POOP `Str` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` |

### No `len` — `poop/validators/no_len.py`

| Call | Reason | Substitute |
|---|---|---|
| `len(x)` | free function with procedural look | `x.len()` |

### No `abs` — `poop/validators/no_abs.py`

| Call | Reason | Substitute |
|---|---|---|
| `abs(x)` | free function with procedural look | `x.abs()` |

### No `hash` — `poop/validators/no_hash.py`

| Call | Reason | Substitute |
|---|---|---|
| `hash(x)` | free function with procedural look | `x.hash()` |

### No `isinstance` — `poop/validators/no_isinstance.py`

| Call | Reason | Substitute |
|---|---|---|
| `isinstance(x, T)` | free function with procedural look | `x.is_instance(T)` |

### No `repr` — `poop/validators/no_repr.py`

| Call | Reason | Substitute |
|---|---|---|
| `repr(x)` | free function with procedural look | `x.repr()` |

### No `ascii` — `poop/validators/no_ascii.py`

| Call | Reason | Substitute |
|---|---|---|
| `ascii(x)` | free function with procedural look | `x.ascii()` |

### No `issubclass` — `poop/validators/no_issubclass.py`

| Call | Reason | Substitute |
|---|---|---|
| `issubclass(A, B)` | free function with procedural look | `A.is_subclass(B)` |

### No `callable` — `poop/validators/no_callable.py`

| Call | Reason | Substitute |
|---|---|---|
| `callable(x)` | free function with procedural look | `x.callable()` |

### No `id` — `poop/validators/no_id.py`

| Call | Reason | Substitute |
|---|---|---|
| `id(x)` | free function with procedural look | `x.id()` |

### No `all` — `poop/validators/no_all.py`

| Call | Reason | Substitute |
|---|---|---|
| `all(col)` | free function with procedural look | `col.all(block)` |

### No `any` — `poop/validators/no_any.py`

| Call | Reason | Substitute |
|---|---|---|
| `any(col)` | free function with procedural look | `col.any(block)` |

### No `min`/`max` — `poop/validators/no_min.py`, `poop/validators/no_max.py`

| Call | Reason | Substitute |
|---|---|---|
| `min(a, b)` | free function with procedural look | `a.min(b)` (binary, on `Int`/`Float`) |
| `min(iterable)` | free function with procedural look | `iterable.min()` |
| `min(iterable, key=fn)` | free function with procedural look | `iterable.min(key=fn)` |
| `min(iterable, default=x)` | free function with procedural look | `iterable.min(default=x)` |
| `min(a, b, c, ...)` | free function with procedural look | `[a, b, c].min()` or chain `a.min(b).min(c)` |

`max` mirrors `min` exactly. The iterable form lives on
`_IterableMixin` (covers `List`, `Tuple`, `Set`, `FrozenSet`,
`Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`, `Zip`)
plus direct implementations on `Str` (smallest/largest character)
and `Dict` (smallest/largest key). Empty iterable without `default`
raises `ValueError`, mirroring Python.

### No `bin`/`hex`/`oct` — `poop/validators/no_bin.py`

| Call | Reason | Substitute |
|---|---|---|
| `bin(n)` | free function with procedural look | `n.bin()` |
| `hex(n)` | free function with procedural look | `n.hex()` |
| `oct(n)` | free function with procedural look | `n.oct()` |

### No `chr`/`ord` — `poop/validators/no_chr.py`

| Call | Reason | Substitute |
|---|---|---|
| `chr(n)` | free function with procedural look | `n.chr()` |
| `ord(c)` | free function with procedural look | `c.ord()` |

### No `divmod` — `poop/validators/no_divmod.py`

| Call | Reason | Substitute |
|---|---|---|
| `divmod(a, b)` | free function with procedural look | `a.divmod(b)` |

### No `pow` — `poop/validators/no_pow.py`

| Call | Reason | Substitute |
|---|---|---|
| `pow(a, b)` | free function with procedural look | `a.pow(b)` |

### No `getattr` — `poop/validators/no_getattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `getattr(x, name)` | free function with procedural look | `x.get_attr(name)` |
| `getattr(x, name, default)` | free function with procedural look | `x.get_attr(name, default)` |

### No `hasattr` — `poop/validators/no_hasattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `hasattr(x, s)` | free function with procedural look | `x.has_attr(s)` |

### No `format` — `poop/validators/no_format.py`

| Call | Reason | Substitute |
|---|---|---|
| `format(x, spec)` | free function with procedural look | `x.format(spec)` |

### `zip` → `Zip` — `poop/transformers/zip.py`

`zip(a, b, ...)` and `zip(a, b, strict=True)` are rewritten by `ZipTransformer` to `_poop_zip(...)`, which returns a `Zip` object.

`Zip` (`poop/types/zip.py`) is a lazy iterable POOP type mirroring Python's `zip` exactly: accepts any number of iterables, stops at the shortest, raises `ValueError` when `strict=true` and lengths differ, and raises `TypeError` eagerly on construction if any source is not iterable (matches Python's `'X' object is not iterable`). It inherits `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any` from `_IterableMixin`. Every `_IterableMixin` type and `Dict` expose `.zip(*others, strict=false) -> Zip` as a convenience method.

### `enumerate` → `Enumerate` — `poop/transformers/enumerate.py`

`enumerate(col)` and `enumerate(col, start)` are rewritten by `EnumerateTransformer` to `_poop_enumerate(col)` / `_poop_enumerate(col, start)`, which returns an `Enumerate` object.

`Enumerate` (`poop/types/enumerate.py`) is a lazy iterable POOP type. It wraps any iterable (including `Dict`) and yields `Tuple(Int(index), item)` pairs on demand, raising `TypeError` eagerly on construction if the source is not iterable. It inherits `do`, `map`, `filter`, `filter_false`, `find`, `sum`, `all`, `any` from `_IterableMixin`. Every collection type exposes `.enumerate(start=Int(0)) -> Enumerate` as a convenience method. `Dict.enumerate()` iterates over keys, consistent with Python's `enumerate(dict)`.

### No `iter`/`next` — `poop/validators/no_iter.py`

| Call | Reason | Substitute |
|---|---|---|
| `iter(col)` | iterator protocol with procedural look | `col.iter()` |
| `next(it)` | same | `it.next()` |
| `aiter(col)` | async variant | `col.iter()` |
| `anext(it)` | async variant | `it.next()` |

Every collection exposes `.iter()` returning a specialized one-shot iterator that mirrors Python's iterator types (`list_iterator`, `tuple_iterator`, `set_iterator` (shared by `set` and `frozenset`, as in CPython), `dict_keyiterator`, `str_iterator`, `range_iterator`, `bytes_iterator`, `bytearray_iterator`, `memory_iterator`). All inherit from `_IteratorBase` (`poop/types/_iterator_base.py`), expose `.next()` and `.do(block)`, and raise `StopIteration` on exhaustion — catchable via `Try(lambda: it.next()).except_(StopIteration, handler).run()`.

`Enumerate` and `Zip` are their own iterators (`x.iter() is x`, mirroring Python's `iter(zip(...)) is zip(...)`). They expose `.next()` consuming a lazy internal generator one-shot, while `.do()` keeps the existing restartable behaviour.

`Dict.iter()` returns `DictKeyIterator`, mirroring `iter(dict)` in Python. `Dict.values().iter()` returns `DictValueIterator`; `Dict.items().iter()` returns `DictItemIterator`. Each view also exposes `.reversed()` returning the matching reverse iterator (`DictReverseKeyIterator`, `DictReverseValueIterator`, `DictReverseItemIterator`).

### Dict views — `poop/types/dict_keys.py`, `poop/types/dict_values.py`, `poop/types/dict_items.py`

`Dict.keys()`, `Dict.values()`, and `Dict.items()` return **live view** objects mirroring Python's `dict_keys`, `dict_values`, and `dict_items` exactly. They reflect mutations to the underlying dict.

| View | iter | set ops | comparison | mapping |
|---|---|---|---|---|
| `DictKeys` | `DictKeyIterator` | `\|`, `&`, `-`, `^` → `Set`; `isdisjoint` | `__eq__`, `__le__`, `__lt__`, `__ge__`, `__gt__` (set semantics) | `mapping()` → `MappingProxy` |
| `DictValues` | `DictValueIterator` | none (values may be unhashable) | inherits `Object` identity (Python parity) | `mapping()` |
| `DictItems` | `DictItemIterator` (yields `Tuple(k, v)`) | `\|`, `&`, `-`, `^` → `Set` of `Tuple`; `isdisjoint` | full set semantics like `DictKeys` | `mapping()` |

All three views are unhashable (`__hash__ = None`), expose `len()`/`includes()`/`__contains__`, and support `__reversed__`. `DictKeys` and `DictValues` inherit `_IterableMixin`; `DictItems` also inherits the mixin and yields `Tuple(k, v)` from `__iter__`. To materialize a view as a `List`, use `list(view)` — the `ListTransformer` rewrites the call to `_poop_list_from(view)`, which accepts any iterable.

### MappingProxy — `poop/types/mapping_proxy.py`

`MappingProxy` is a read-only wrapper over a `Dict` mirroring `types.MappingProxyType`. Returned by `view.mapping()` on the three dict views. Exposes read methods (`at`, `get`, `keys`, `values`, `items`, `len`, `includes`, `iter`, `copy`, `reversed`, `__or__` returning `Dict`) but no mutation methods. Equality with `Dict` and `MappingProxy`. Unhashable.

### No `setattr`/`delattr` — `poop/validators/no_setattr.py`

| Call | Reason | Substitute |
|---|---|---|
| `setattr(obj, name, val)` | free function with procedural look | `obj.set_attr(name, val)` |
| `delattr(obj, name)` | same | `obj.del_attr(name)` |

### No introspection — `poop/validators/no_introspection.py`

| Call | Reason |
|---|---|
| `globals()` | scope introspection — state lives in instances |
| `locals()` | same |
| `vars(obj)` | exposes raw Python-native slot values (`_value`, `_items`, `_data`) that are not POOP objects — breaks encapsulation and the "all methods return POOP types" rule; no clean substitute |

### No `dir` — `poop/validators/no_dir.py`

| Call | Reason | Substitute |
|---|---|---|
| `dir(obj)` | free function with procedural look | `obj.dir()` |

### No `type` — `poop/validators/no_type.py`

| Call | Reason | Substitute |
|---|---|---|
| `type(x)` | free function returning a raw class object that is not a POOP value; the three-arg form is a metaprogramming escape — type dispatch belongs in methods | `x.class_name()` or polymorphism |

### No `exec`/`eval`/`compile` — `poop/validators/no_exec.py`

| Call | Reason |
|---|---|
| `exec(code)` | metaprogramming — not allowed in POOP |
| `eval(expr)` | same |
| `compile(src, ...)` | same |

### No `exit`/`quit` — `poop/validators/no_exit.py`

| Call | Reason |
|---|---|
| `exit()` | process control — no POOP equivalent |
| `quit()` | same |

### No `breakpoint` — `poop/validators/no_breakpoint.py`

| Call | Reason |
|---|---|
| `breakpoint()` | Python-specific debugging — no POOP equivalent |

### No `help` — `poop/validators/no_help.py`

| Call | Reason |
|---|---|
| `help(obj)` | interactive escape hatch (opens the Python pager) exposing wrapper internals — no POOP equivalent |

### No `input` — `poop/validators/no_input.py`

| Call | Reason | Substitute |
|---|---|---|
| `input(prompt)` | free function with procedural look | `prompt.input()` (`poop/types/string.py`) |

Symmetric to `Object.print()` — the receiver is what gets shown. Scoped to `Str` (not `Object`) since non-string receivers as prompts are meaningless. `EOFError` propagates raw, catchable via `Try(lambda: prompt.input()).except_(EOFError, handler).run()`.

### No `open` → `Path` — `poop/validators/no_open.py`, `poop/transformers/path.py`

| Call | Reason | Substitute |
|---|---|---|
| `open(path, ...)` | free function with procedural look | `Path('foo').read_text()` / `write_text(content)` (`poop/types/path.py`) |

`Path` (`poop/types/path.py`) wraps `pathlib.Path` and exposes filesystem I/O as message passing. Exposed as a namespace-only binding via the `NAMESPACE` dict in `poop/transformers/path.py` (no AST rewrite), in the same family as `Try` / `With`. `Path` accepts `Str | Path` in the constructor (idempotent), supports `__truediv__` for joining (`Path('dir') / 'file.txt'`), and orders by the underlying `pathlib.Path`.

| Method | Returns | Notes |
|---|---|---|
| `read_text()` / `write_text(content)` | `Str` / `Int` (bytes written) | UTF-8 only |
| `read_bytes()` / `write_bytes(data)` | `Bytes` / `Int` (bytes written) | |
| `exists()` / `is_file()` / `is_dir()` / `is_symlink()` / `is_absolute()` | `Boolean` | direct delegation |
| `mkdir(mode, parents, exist_ok)` / `rmdir()` / `unlink(missing_ok)` / `touch(mode, exist_ok)` | `NoneClass` | mutate, return `none` |
| `resolve()` / `absolute()` / `rename(target)` / `replace(target)` | `Path` | navigation |
| `joinpath(*others)` / `with_name(n)` / `with_suffix(s)` / `with_stem(s)` / `relative_to(other)` | `Path` | navigation |
| `as_posix()` / `as_uri()` | `Str` | |
| `iterdir()` | `PathIterator` | lazy, one-shot — `pathlib.iterdir` returns a generator |
| `glob(pattern)` / `rglob(pattern)` | `Map` | `pathlib.glob`/`rglob` already return a `map`; POOP `Map` wraps it with `Path._from_pathlib` |
| `Path.cwd()` / `Path.home()` | `Path` | classmethods |
| Properties: `name` / `stem` / `suffix` | `Str` | mirror `pathlib` |
| Properties: `parts` / `parents` | `Tuple[Str]` / `Tuple[Path]` | |
| Property: `parent` | `Path` | |

`PathIterator` (`poop/types/path_iterator.py`) inherits `_IteratorBase` and `_IterableMixin` — it exposes `next()` / `do(block)` and gains `map` / `filter` / `find` / `all` / `any` / `reduce` / `sum` / `min` / `max` / `enumerate` / `zip` from the mixin. It is one-shot (the underlying `pathlib` generator is consumed lazily).

Out of v1 (filed if demand appears): `open(mode)` returning a POOP `File`, `stat()` / `lstat()`, `owner()` / `group()`, datetime-typed `mtime`, full `PurePath` hierarchy, non-UTF-8 encodings.

### No `del` — `poop/validators/no_del.py`

| AST node | Reason |
|---|---|
| `ast.Delete` | objects have no explicit destruction — simply do not delete |

### No `import` — `poop/validators/no_import.py`

| AST node | Reason |
|---|---|
| `ast.Import` | POOP injects its stdlib namespaces (`math`, `os`, `json`, …) — `import` would bind the raw CPython module over the wrapper layer |
| `ast.ImportFrom` | same — the names are already in scope; `from os import getcwd` would leak raw Python values |

### No `_poop_*` prefix — `poop/validators/no_poop_prefix.py`

| AST node | Reason |
|---|---|
| `ast.Name` with `id` starting in `_poop_` | mangled identifier reserved for the runtime — rewriters target it, user code must not |
| `ast.Attribute` with `attr` starting in `_poop_` | same — keeps the runtime helpers reachable for the rewritten AST but invisible to handwritten code |

Every type wrapper (`Int`, `List`, `Object`, …) lives in `DEFAULT_NAMESPACE` under a `_poop_*` key (`_poop_int`, `_poop_list_cls`, `_poop_object`, …) so the rewritten AST resolves them at runtime. This validator stops user code from referencing the same names directly, preserving the abstraction that POOP types pass as their Python builtin counterparts.

### No namespace shadow — `poop/validators/no_namespace_shadow.py`

| AST node | Reason |
|---|---|
| `ast.Assign` with target `ast.Name` in the protected set | reassigning a namespace name (`math = 42`) breaks every later call to `math.sqrt(…)` |
| `ast.AnnAssign` with target `ast.Name` in the protected set | annotated form (`math: int = 42`) — same problem |
| `ast.AugAssign` with target `ast.Name` in the protected set | augmented form (`math += 1`) — same problem |
| `ast.ClassDef` whose `name` is in the protected set | `class math: …` binds `math` at module level, shadows the namespace |
| Unpacking targets (`ast.Tuple` / `ast.List` / `ast.Starred`) holding a protected name | tuple unpacking (`math, x = 1, 2`) still rebinds the name |
| `def`/`async def`/`lambda` parameters in the protected set | a parameter named after a binding (`def m(self, math): …`, `lambda math: …`) shadows it inside the body and fails confusingly |

The **protected set** is computed dynamically from `DEFAULT_NAMESPACE` (filtered to non-`_poop_*` entries) at validator instantiation time. Today: `Browser`, `Connection`, `Context`, `Cursor`, `Date`, `DateTime`, `Decimal`, `HMAC`, `Hash`, `Match`, `MimeTypes`, `Path`, `Pattern`, `PrettyPrinter`, `Random`, `Row`, `Shlex`, `Time`, `TimeDelta`, `TimeZone`, `TopologicalSorter`, `Try`, `UUID`, `With`, `binascii`, `bisect`, `copy`, `datetime`, `decimal`, `errno`, `fnmatch`, `getpass`, `glob`, `graphlib`, `hashlib`, `heapq`, `hmac`, `json`, `math`, `mimetypes`, `pprint`, `random`, `re`, `secrets`, `shlex`, `sqlite3`, `tomllib`, `uuid`, `webbrowser`. As new namespace mirrors land (`uuid`, …), they protect themselves automatically — no changes to this validator.

What the validator **does not** catch: method names inside classes (`class Calc: def math(self): …`), which bind as attributes, not in the namespace scope.

### No builtin shadow — `poop/validators/no_builtin_shadow.py`

Reuses the namespace-shadow `_Visitor` over a fixed set of the 17 lowercase builtin names the type transformers rewrite to mangled `_poop_*` globals: `bool`, `int`, `float`, `complex`, `str`, `bytes`, `bytearray`, `memoryview`, `list`, `tuple`, `dict`, `set`, `frozenset`, `range`, `slice`, `enumerate`, `zip`. Rebinding one (assignment, class name, or `def`/`lambda` parameter) would silently retarget the interpreter's internals — `str = "x"` replaces the literal constructor, `def m(self, dict)` makes the body operate on the internal `Dict` class — so the validator rejects it with `'<name>' is a POOP builtin name; it cannot be rebound`. Using the names as constructors (`int("5")`) is unaffected.

### No `sum` — `poop/validators/no_sum.py`

| Call | Reason | Substitute |
|---|---|---|
| `sum(col)` | free function with procedural look | `col.sum()` |

Available on `List`, `Tuple`, `Set`, `FrozenSet`, and `Range`.

### No `map` / `filter` — `poop/validators/no_map.py`, `poop/validators/no_filter.py`

| Call | Reason | Substitute |
|---|---|---|
| `map(func, col)` | free function with procedural look | `col.map(block)` returning `Map` (lazy) |
| `filter(func, col)` | free function with procedural look | `col.filter(block)` returning `Filter` (lazy) |

`col.map(block)` returns a `Map` and `col.filter(block)` returns a
`Filter` — both lazy iterators in the same family as `Enumerate` and
`Zip`. The block is applied on demand as the result is consumed.
Materialization is via the target type's constructor:

```python
list(items.map(lambda x: x + 1))           # -> List
tuple(items.filter(lambda x: x > 0))       # -> Tuple
set(items.map(lambda x: x.lower()))        # -> Set
bytes(items.map(lambda x: x.code()))       # -> Bytes
```

In Python tests (where the transformer doesn't run), construct via
varargs unpack: `List(*items.map(...))`. Methods that consume the
iterator (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`)
work on `Map`/`Filter` directly via `_IterableMixin`.

### No `round` — `poop/validators/no_round.py`

| Call | Reason | Substitute |
|---|---|---|
| `round(x)` | free function with procedural look | `x.round()` |
| `round(x, n)` | free function with procedural look | `x.round(n)` |

Available on `Int` and `Float`.

### No `sorted` / `reversed` — `poop/validators/no_sorted.py`, `poop/validators/no_reversed.py`

| Call | Reason | Substitute |
|---|---|---|
| `sorted(col)` | free function with procedural look | `col.sorted()` |
| `reversed(col)` | free function with procedural look | `col.reversed()` |

### No `in` / `not in` — `poop/validators/no_in.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Compare` | op is `ast.In` | `x in col` has a procedural look | `col.includes(x)` |
| `ast.Compare` | op is `ast.NotIn` | `x not in col` has a procedural look | `col.includes(x).not_()` |

### No subscript — `poop/validators/no_subscript.py`

| AST node | Condition | Reason | Substitute |
|---|---|---|---|
| `ast.Subscript` | no `ast.Slice` involved | `obj[key]` looks like an operator | `obj.at(key)` |
| `ast.Subscript` | a bare `ast.Slice` or an `ast.Tuple` containing one (extended slices like `obj[i:j, k:l]`) | `obj[1:3]` looks like an operator | `obj.slice(start, stop)` |

### No comprehension — `poop/validators/no_comprehension.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.ListComp` / `ast.SetComp` / `ast.DictComp` / `ast.GeneratorExp` | implicit iteration with procedural look | `col.map(block)`, `col.filter(block)` |

## Explicitly allowed

Constructs considered for blocking but decided to allow by design.

### Augmented assignment (`+=`, `-=`, `*=`, …)

`x += 1` is syntactic sugar for `x = x + 1`. Both forms rebind the variable using the same arithmetic operation — there is no message-passing substitute that would be more idiomatic. Blocking `+=` would be a purely cosmetic restriction without a principled rationale. `ast.AugAssign` is intentionally not blocked.

### `super`

`super()` is the standard way to delegate to a parent method in both Python and Smalltalk. Without it, subclasses cannot extend parent behaviour — inheritance breaks entirely. There is no message-passing substitute. Allowed.

### `property` / `classmethod` / `staticmethod`

These are class-definition decorators, not runtime operations on values. They define how a method is bound, not what it does. Blocking them would prevent idiomatic class definitions without a principled POOP substitute. Allowed.

### `help`

`help()` is a development tool — it prints documentation for inspection at the REPL or during exploration. It carries no program logic and has no message-passing equivalent that would be more expressive. Allowed.

### Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)

`a + b`, `a == b`, `a < b` and their siblings are allowed. These are `ast.BinOp` and `ast.Compare` nodes — the same syntactic family as `+=`, which is already explicitly allowed.

The rationale mirrors Smalltalk: binary messages (`+`, `-`, `*`, …) are the idiomatic way to express arithmetic and comparison. Blocking them would force `a.add(b)`, `a.lt(b)` etc., which is more verbose without being more expressive or principled. The key asymmetry is with *unary* operators: `-a` (USub), `~a` (Invert) have named message equivalents (`a.negated()`, `a.bit_invert()`) and carry no ergonomic benefit in infix form, so they are blocked. Binary forms have no principled substitute.

### Numeric comparisons follow CPython's numeric tower

`Int(1) == Float(1.0)` → `true`. `Int(1) == Complex(1+0j)` → `true`. `True == 1` → `true`. POOP's numeric types (`Int`, `Float`, `Complex`, `Boolean`) compare by value across the tower exactly like CPython, in both directions — `Boolean` is part of it because `bool` is an `int` subclass in Python.

Comparison across *non-numeric* types stays `false` (an `Int` is never equal to a `Str`), mirroring CPython. Each `__eq__` returns `NotImplemented` for operands outside its numeric tower so Python's reflected-comparison fallback applies, keeping the relation symmetric.

## Active types

### Object — `poop/types/object.py`

Concrete root of all POOP types. The table below highlights the universal methods that map directly onto Smalltalk messages — it is **not exhaustive**. The full API also includes `if_none`, `if_not_none`, `hash`, `id`, `callable`, `is_subclass`, `repr`, `ascii`, `format`, `has_attr`, `set_attr`, `del_attr`, and `print` (see `poop/types/object.py` for signatures).

| Smalltalk message | Method | Behavior |
|---|---|---|
| `isNil` | `is_none()` | always `false` for Object |
| `notNil` | `not_none()` | always `true` for Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` as `Str` |
| `perform:` | `get_attr(name)` | `getattr` with optional default |
| — | `dir()` | sorted `List` of `Str` attribute names (`builtins.dir(self)`) |

`__str__` returns `"<ClassName>"` as fallback; `__repr__` delegates to `__str__`.

#### `is_instance` and raw Python types

`obj.is_instance(T)` accepts a raw Python `type` (e.g. `Int`, `Str`, `Boolean`) — not a POOP-level "Class" object. This is a deliberate primitive leak: POOP has no first-class metaclass or class-object type, so there is nothing more idiomatic to pass. The same tradeoff applies to exception types in `Try.except_(ValueError, handler)` and context managers in `With`. The message-passing form (`obj.is_instance(...)`) is preserved; only the argument is a native Python type rather than a POOP wrapper.

### NoneClass — `poop/types/none.py`

`NoneClass(Object)` with singleton `none`. Transformer rewrites `ast.Constant(value=None)` → `_poop_none`.

| Method | `Object` | `NoneClass` |
|---|---|---|
| `is_none()` | `false` | `true` |
| `not_none()` | `true` | `false` |
| `if_none(block)` | does not execute | executes block |
| `if_not_none(block)` | executes passing `self` | does not execute |

`__bool__` returns `False`. `__str__` returns `"None"`.

`ReturnTransformer` (`poop/transformers/return_.py`) keeps the implicit-return path on the POOP side: a bare `return` becomes `return _poop_none`, and a function body that does not end in `return`/`raise` gets a trailing `return _poop_none` appended, so a void method answers the `none` singleton instead of raw `NoneType`. `__init__` is skipped (CPython requires it to return real `None`).

`VarargsTransformer` (`poop/transformers/varargs.py`) keeps variadic parameters on the POOP side: a method with `*args` / `**kwargs` gets a prologue (`args = _poop_tuple_from(args)`, `kw = _poop_dict_from_kwargs(kw)`) so `args` is a POOP `Tuple` and `kw` a POOP `Dict` (with `Str` keys) instead of a raw `tuple`/`dict`. Variadic lambdas wrap their body in a nested lambda that receives the converted values.

`UnpackTransformer` (`poop/transformers/unpack.py`) keeps starred unpacking on the POOP side: CPython's `UNPACK_EX` builds the rest-collection of `c, *rest = xs` as a raw `list`, so after each assignment containing a `*target` the transformer appends `target = _poop_list_from(target)` — one per starred name, handling nested (`a, (b, *inner) = …`) and attribute (`a, *self.rest = …`) targets.

### Boolean — `poop/types/boolean.py`

`Boolean(Object, ABC)` with private subclasses `_TrueClass` and `_FalseClass`. Singletons `true`/`false` replace `True`/`False` via transformer.

| Smalltalk message | Method |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |
| `assert:` | `assert_(message)` (on `Object`, not just `Boolean`) | raises `AssertionError(message)` if `bool(self)` is falsy; returns `self` otherwise |

### Block — `poop/types/block.py` + `poop/transformers/block.py`

`Block` is a first-class object wrapping a callable. In Smalltalk, `[...]` syntax creates a block; in POOP every `lambda` expression is automatically rewritten to `Block(lambda: ...)` by the transformer. This makes `lambda` the idiomatic block literal — the `Block(...)` wrapper is transparent to the programmer.

`while_true` and `while_false` live on `Block`, not on `Boolean`. The receiver is the condition block — the object whose value determines whether the loop continues. This matches Smalltalk semantics (`[cond] whileTrue: [body]`) and eliminates the philosophical problem of the receiver being irrelevant.

| Smalltalk message | POOP idiom |
|---|---|
| `[cond] whileTrue: [body]` | `(lambda: cond).while_true(lambda: body)` |
| `[cond] whileFalse: [body]` | `(lambda: cond).while_false(lambda: body)` |
| `[block] value` | `(lambda: expr)()` |
| `[block] value: arg` | `(lambda x: expr)(arg)` |

> **Why lambda, not `[...]`?** Python has no block literal syntax. `lambda` is the closest equivalent — a deferred expression. The transformer intercepts every `ast.Lambda` and wraps it in `Block(...)` transparently, so the programmer writes plain lambdas and gets first-class POOP block objects without ever naming `Block` explicitly.

### Collection iterable methods — `poop/types/_iterable_mixin.py`

`List`, `Tuple`, `Set`, `FrozenSet`, `Range`, `Bytes`, `ByteArray`, `MemoryView`, `Enumerate`, `Zip`, `DictKeys`, `DictValues`, and `DictItems` all inherit the following methods from `_IterableMixin`:

| Smalltalk message | POOP method | Behavior |
|---|---|---|
| `do:` | `do(block)` | visits each element; returns `none` (substitute for `for` loop) |
| `collect:` | `map(block)` | returns `Map` (lazy); materialize via `list(...)`/`tuple(...)`/etc. |
| `select:` | `filter(block)` | returns `Filter` (lazy); same materialization |
| `reject:` | `filter_false(block)` | returns `Filter` (lazy) with the predicate inverted |
| `detect:` | `find(block)` | first element satisfying block, or POOP `none` |
| `inject:into:` | `reduce(init, block)` | fold with required initial value; returns accumulated result |
| — | `sum()` | sum of elements; returns `Int(0)` for empty collection |
| — | `min(key=None, default=...)` | smallest element; mirrors Python `min` |
| — | `max(key=None, default=...)` | largest element; mirrors Python `max` |
| — | `all(block)` | `true` if block holds for every element |
| — | `any(block)` | `true` if block holds for at least one element |
| — | `enumerate(start=Int(0))` | returns an `Enumerate` of `Tuple(Int(i), item)` pairs |
| — | `zip(*others, strict=false)` | returns a `Zip` of `Tuple(...)` |

`map`/`filter`/`filter_false` are **lazy** — they return `Map`/`Filter` iterators (same family as `Enumerate`/`Zip`) regardless of the receiver's type, mirroring Python's `map`/`filter` builtins. The block runs only as the result is consumed. To materialize, pass the lazy result to a constructor: `list(col.map(f))`, `tuple(col.filter(g))`, `set(col.map(f))`, `bytes(col.map(g))`. Methods that consume the iterator (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`) work on `Map`/`Filter` directly without materialization.

`Dict.do` is not from the mixin — it passes `Tuple(key, value)` pairs to the block instead of plain elements. `Bytes` and `ByteArray` override `find` for substring search (different semantics from the mixin's element-finding `find`).

### Map / Filter — `poop/types/map.py`, `poop/types/filter.py`

`Map` and `Filter` are lazy iterator types in the same family as `Enumerate` and `Zip`. They wrap a source iterable and a block, and apply the block on demand:

- `Map(source, block)` yields `block(item)` for each item.
- `Filter(source, block)` yields `item` when `block(item)` is truthy.

Both inherit `_IterableMixin` so chains like `col.map(f).filter(g).sum()` keep iterating once through the source. Both expose `.next()` (one-shot, like `Enumerate`/`Zip`) and `__iter__` (returns a fresh generator — restartable when the source is restartable).

`Map` and `Filter` are internal — they have no transformer and are not bound in `DEFAULT_NAMESPACE`. User code reaches them exclusively through the mixin's `.map(block)` / `.filter(block)` / `.filter_false(block)` methods. Python tests that import directly from `poop.types.map` / `poop.types.filter` may construct them as `Map(source, block)` / `Filter(source, block)`.

### Range — `poop/types/range.py`

`Range(Object)` represents a closed integer interval [start, stop]. Created via `range(start, stop)` (rewritten to `_poop_range(...)` by the transformer).

| POOP method | Behavior |
|---|---|
| `do(block)` | see collection iterable methods above |
| `map(block)` | transforms → `Map` (lazy) |
| `filter(block)` | filters → `Filter` (lazy) |
| `filter_false(block)` | filters inverse → `Filter` (lazy) |
| `find(block)` | first satisfying, or POOP `none` |
| `iter()` | returns a one-shot `RangeIterator` |
| `len()` | returns `Int` |
| `at(index)` | returns the value at `index` as `Int` |
| `slice(start, stop, step=None)` | slice → `List` |
| `slice(slice_obj)` | slice via `Slice` value object → `List` |
| `reversed()` | returns reversed `Range` |
| `includes(value)` | `true` if `value` is in the range |
| `count(value)` | number of occurrences (always `0` or `1`) |
| `index(value)` | position of `value`, or raises `ValueError` |
| `start` / `stop` / `step` | properties exposing the underlying `Int` bounds |

### Object.print — `poop/types/object.py`

All POOP objects inherit `print()` from `Object`. `List` and `Tuple` override to support `sep`.

| Message | Behavior |
|---|---|
| `obj.print()` | prints `str(obj)` followed by `\n`; returns `None` |
| `obj.print(end="")` | controls the terminator |
| `obj.print(flush=True)` | forces buffer flush |
| `list.print(sep=", ")` | `List`/`Tuple`: joins elements with `sep` (default `" "`) |

`"".print()` prints a blank line.

### Error — `poop/types/error.py`

`Error(Object)` wraps a caught Python exception. Handlers in `Try.except_` always receive an `Error` object.

| Method | Behavior |
|---|---|
| `message()` | returns exception message as `Str` |
| `kind()` | returns exception class name as `Str` |

`__str__` returns `"Error(<exception>)"`.

### Try — `poop/types/try_.py`

`Try(Object)` implements deferred try/except/finally as a message-passing builder. The block is executed lazily — only when `.run()` or `.finally_()` is called.

| Message | Method | Behavior |
|---|---|---|
| `[block] on: ExcType do: handler` | `Try(block).except_(ExcType, handler)` | registers a handler; chainable |
| `[block] ensure: finallyBlock` | `Try(block).finally_(block)` | sets finally block **and** executes |
| *(terminal)* | `.run()` | executes without finally block |

`exc_type` is a native Python class (`ValueError`, `KeyError`, …) — the only deliberate primitive leak. Unhandled exceptions are always re-raised. Multiple `.except_()` calls are matched in order.

> **Tradeoff**: `exc_type` must be a native Python exception class. Mirroring Python's full hierarchy (~100+ classes) into POOP types is impractical. The handler always receives an `Error` wrapper regardless.

`Try` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/try_.py` — namespace-only, no AST rewrite.

### With — `poop/types/with_.py`

`With(Object)` implements the context manager protocol as a message-passing builder. The context manager block is executed lazily — only when `.do()` is called. A `With` (and `AsyncWith`) is single-use: `.do()` releases its captured block once it runs, so re-invoking `.do()` raises `RuntimeError` rather than re-running — mirroring `Try`'s single-use semantics and avoiding retaining the closure (and anything it captured) past execution.

| Message | Method | Behavior |
|---|---|---|
| `[block] value: aResource` | `With(lambda: cm).do(lambda resource: body)` | acquires resource via `__enter__`, runs body, calls `__exit__` |

The context manager object must implement Python's `__enter__`/`__exit__` protocol — a deliberate primitive leak, consistent with `Try` using native exception types. Exceptions propagate via the standard `__exit__` return value: if `__exit__` returns falsy, the exception is re-raised; truthy suppresses it.

> **Tradeoff**: context managers must implement Python's native protocol (`__enter__`/`__exit__`). POOP cannot redefine resource acquisition semantics without reimplementing every standard context manager (files, locks, etc.), which is impractical.

`With` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/with_.py` — namespace-only, no AST rewrite.

### io + StringIO + BytesIO — `poop/types/io.py` + `poop/transformers/io.py`

`io` exposes the in-memory buffers `StringIO` / `BytesIO` plus the seek constants. It survives the removal of the stdlib mirrors for the same reason `Path` does: both are POOP-specific entry points rather than library surface — `Path` is the substitute the `no_open` ban points at, and `io` is the in-memory half of the same story. Disk I/O still goes through `Path.read_*` / `write_*`; POOP has no file-object abstraction and does not mirror Python's file protocol.

| Operation | Returns | Notes |
|---|---|---|
| `StringIO(initial_value=none, newline=none)` | `StringIO` | in-memory text buffer |
| `BytesIO(initial_bytes=none)` | `BytesIO` | in-memory binary buffer |
| `.read(size=none)` / `.readline(size=none)` | `Str` / `Bytes` | per buffer type |
| `.write(s)` | `Int` | characters/bytes written |
| `.getvalue()` | `Str` / `Bytes` | |
| `.seek(pos, whence=none)` / `.tell()` | `Int` | `whence` defaults to `SEEK_SET` |
| `.truncate(size=none)` | `Int` | new size |
| `.close()` | `none` | both buffers are context managers — `With(lambda: StringIO()).do(…)` |
| `io.SEEK_SET` / `SEEK_CUR` / `SEEK_END` / `DEFAULT_BUFFER_SIZE` (class attrs) | `Int` | |
| `io.IOBase` / `RawIOBase` / `BufferedIOBase` / `TextIOBase` (class attrs) | raw type | for `is_instance` against raw Python streams |
| `io.UnsupportedOperation` / `BlockingIOError` (class attrs) | error class | for `Try.except_(…)` |

`io`, `StringIO` and `BytesIO` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/io.py` — namespace-only, no AST rewrite.

### Slice — `poop/types/slice.py` + `poop/transformers/slice.py`

`slice(start, stop, step=None)` is **transformed** by `SliceTransformer` into a call to the POOP `Slice` constructor — the same approach as `range` → `Range`. The free builtin is not forbidden; it is rewritten transparently.

`obj.slice(start, stop, step=None)` is also accepted directly on every sequence type. Both forms are equivalent at runtime.

`Slice` is a first-class immutable POOP type (`poop/types/slice.py`) — hashable, comparable with `==`/`!=`, and reusable across collections.

| Method | Returns | Notes |
|---|---|---|
| `Slice(start, stop)` | `Slice` | Two-arg constructor |
| `Slice(start, stop, step)` | `Slice` | Three-arg constructor |
| `.start()` | `Int` | |
| `.stop()` | `Int` | |
| `.step()` | `Int \| NoneClass` | POOP `none` when not set |
| `.indices(length)` | `Tuple(Int, Int, Int)` | Normalised start/stop/step for a sequence of the given length; mirrors Python's `slice.indices()` |

`obj.slice(s: Slice)` overload is available on every sequence type in addition to the positional form:

| Type | Returns |
|---|---|
| `Str` | `Str` |
| `List` | `List` |
| `Tuple` | `Tuple` |
| `Bytes` | `Bytes` |
| `ByteArray` | `ByteArray` |
| `Range` | `List` |

> `Range.slice` returns `List` (not `Range`) because reconstructing a valid closed interval from sliced `Int` POOP values would require unpacking assumptions about the underlying range step.

## Active transformers

### Int — `poop/transformers/int.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=int)` (except `bool`) | `_poop_int(n)` |
| `ast.UnaryOp(USub, Constant(int))` | `_poop_int(-n)` — collapsed negative literal |
| `ast.Call` with `int(x)` or `int(s, base)` | `_poop_int_from(x)` / `_poop_int_from(s, base)` |

### Float — `poop/transformers/float.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=float)` | `_poop_float(n)` |
| `ast.UnaryOp(USub, Constant(float))` | `_poop_float(-n)` — collapsed negative literal |
| `ast.Call` with `float(x)` | `_poop_float_from(x)` |

### Boolean — `poop/transformers/boolean.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=True)` | `_poop_true` |
| `ast.Constant(value=False)` | `_poop_false` |
| `ast.Call` with `bool(x)` | `_poop_bool_from(x)` |

### None — `poop/transformers/none.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=None)` | `_poop_none` |

### Str — `poop/transformers/string.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=str)` | `_poop_str(s)` |
| `ast.Call` with `str(x)` | `_poop_str_from(x)` |

### Bytes — `poop/transformers/bytes.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=bytes)` | `_poop_bytes(b)` |
| `ast.Call` with `bytes(x)` or `bytes(s, enc)` | `_poop_bytes_from(x)` / `_poop_bytes_from(s, enc)` |

### List — `poop/transformers/list.py`

| AST node | Replacement |
|---|---|
| `ast.List` (Load context) | `_poop_list(*elts)` |
| `ast.Call` with `list(x)` | `_poop_list_from(x)` |

### Tuple — `poop/transformers/tuple.py`

| AST node | Replacement |
|---|---|
| `ast.Tuple` (Load context) | `_poop_tuple(*elts)` |
| `ast.Call` with `tuple(x)` | `_poop_tuple_from(x)` |

### Set — `poop/transformers/set.py`

| AST node | Replacement |
|---|---|
| `ast.Set` | `_poop_set(*elts)` |
| `ast.Call` with `set(x)` | `_poop_set_from(x)` |

### Dict — `poop/transformers/dict.py`

| AST node | Replacement |
|---|---|
| `ast.Dict` (no unpacking) | `_poop_dict_from_pairs(k1, v1, k2, v2, …)` |
| `ast.Call` with `dict(x)` | `_poop_dict_from(x)` — `x` must be `Dict` or iterable of 2-element `Tuple`/`List` pairs |

### Complex — `poop/transformers/complex.py`

| AST node | Replacement |
|---|---|
| `ast.Constant(value=complex)` | `_poop_complex_literal(v)` |
| `ast.BinOp` combining real + imaginary literal | collapsed into `_poop_complex_literal(r+ij)` |
| `ast.Call` with `complex(r, i)` | `_poop_complex_from(r, i)` |

### ByteArray — `poop/transformers/byte_array.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `bytearray(x)` | `_poop_bytearray_from(x)` |

### MemoryView — `poop/transformers/memory_view.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `memoryview(x)` | `_poop_memoryview_from(x)` |

### FrozenSet — `poop/transformers/frozen_set.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `frozenset(x)` | `_poop_frozenset_from(x)` |

### Range — `poop/transformers/range.py`

| AST node | Replacement |
|---|---|
| `ast.Call` with `range(stop)` / `range(start, stop)` / `range(start, stop, step)` | `_poop_range(...)` → `Range` |

### Raise — `poop/transformers/raise_.py`

Intercepts `UppercaseName.raise_(args)` (where `UppercaseName` starts with a capital letter) and rewrites it to a function call that works inside lambdas.

| Pattern | Replacement |
|---|---|
| `ExcType.raise_('msg')` | `_poop_raise(ExcType, 'msg')` |

> **Why not `ast.Raise`?** The transformer generates a function call (`_poop_raise(...)`) instead of an `ast.Raise` statement. Statements are illegal inside `lambda` expressions — POOP's primary block mechanism. This design allows `Try(lambda: KeyError.raise_("msg")).except_(...)` to work correctly.

> **Tradeoff**: `ExcType` must be a Python exception class (not a POOP object). Only uppercase-named receivers are intercepted; lowercase `obj.raise_()` is passed through to the object's own method at runtime.

### Class — `poop/transformers/class_.py`

Implicitly injects POOP `Object` as the base class of every user-defined class that has no explicit base, mirroring how Python 3 makes every class implicitly inherit from `object`.

| Pattern | Replacement |
|---|---|
| `class Foo:` | `class Foo(_poop_object):` |
| `class Foo(object):` | `class Foo(_poop_object):` |
| `class Foo(Object):` | `class Foo(_poop_object):` — backwards-compat for explicit Smalltalk-style declarations |
| `class Foo(Bar):` | unchanged — already has a base |

The POOP `Object` class is injected into `DEFAULT_NAMESPACE` as `_poop_object` so the rewritten AST resolves it at runtime (the mangled name is reserved by `no_poop_prefix`). User-defined classes automatically gain all `Object` methods: `print()`, `is_none()`, `not_none()`, `assert_()`, `class_name()`, `get_attr()`, etc.

> **Tradeoff**: classes that explicitly inherit from native Python types (e.g. `class Foo(Exception):`) are left unchanged — they do not gain POOP `Object` methods, consistent with how `Try` and `Error` interact with the native exception hierarchy.
