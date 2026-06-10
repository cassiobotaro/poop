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
- Callback kwargs route through `poop.types._bridge.bridge`. All originally pending per-namespace consumers are shipped; new namespaces should plug in via the same helper.
- CPython entry points that take `*args, **kwargs` (e.g., `textwrap.wrap`, `logging.basicConfig`, `pprint.pp`) expose their kwargs explicitly in POOP to preserve type information.

### Platform-specific constants

Constants that CPython exposes only on some platforms (`socket.AF_UNIX`, `signal.SIGUSR1`, `resource.RLIMIT_NPROC`) bind to POOP `none` on platforms that lack them — never raise on attribute access, never omit the name entirely. This way user code is portable and falsy-checks (`signal.SIGUSR1.is_none()`) work uniformly.

### Error class exposure

Every exception class that CPython raises through the wrapped surface and that a POOP user might reasonably pass to `Try.except_(...)` is exposed on the wrapping namespace. `json.JSONDecodeError`, `subprocess.CalledProcessError`, `ssl.SSLError`, `urllib.URLError` — all surface. Internal-only error classes (CPython's `_ssl.SSLError` aliases, `_socket.error` aliases) stay hidden.

### Callback kwargs route through `block.bridge`

When a wrapped namespace exposes a callback kwarg (`default=` on `json.dumps`, `object_hook=` on `json.loads`, `predicate=` on `textwrap.indent`, etc.), the user-supplied `Block` runs through `poop.types._bridge.bridge(...)`. The bridge wraps stdlib-supplied arguments into POOP types via `to_poop` before invoking the block, then unwraps the block's return value via `to_python` so the stdlib caller sees the type it asked for. Do not re-implement wrap/unwrap per module — every namespace shares one helper. Use `wrap_args=False` when the stdlib already hands a meaningful POOP-side value; use `unwrap_return=False` when the block's return flows back into POOP-side code that re-wraps at an outer boundary anyway (`json.object_hook` and friends).

### Pull deferred surface only when a caller asks

POOP's stdlib mirrors cover the daily-use surface of each wrapped module; long-tail items (rare-call helpers, debug-only flags, niche per-platform constants) stay out until a real caller surfaces. Surfacing them upfront just inflates the API and creates churn — wait for a concrete use case, then wrap with the same POOP-type-discipline contract as the rest of the namespace. New requests open issues against the project; they should not gate the 1.0 release.

## Permanent divergences from CPython

Surfaces POOP intentionally does not mirror — not deferred, not a backlog item, decided out. User code that wants any of these calls into raw CPython (POOP doesn't sandbox you out of `import`-on-the-Python-side; it just doesn't bless these via the POOP namespace).

### No file-descriptor I/O

POOP file I/O routes through `Path`. The CPython fd-integer ABI (`os.open` / `os.close` / `os.read` / `os.write` / `os.dup` / `os.dup2` / `os.pipe` / `os.fdopen` / `os.closerange` / `os.lseek` / `os.fsync` / `os.fdatasync` / `os.ftruncate` / `os.fchmod` / `os.fchown` / `os.fstat` / `os.openpty` / `os.eventfd*` / `os.memfd_create` / `os.pidfd_open` / `signal.set_wakeup_fd`, etc.) stays out. Same for the `*at`-suffixed dir-fd variants (`os.openat`, `os.linkat`, `os.unlinkat`, `os.symlinkat`, `os.fchmodat`, `os.fchownat`, `os.fstatat`, …). Use `Path` and `With(Path(...).open(...))`.

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

### No f-strings — `poop/validators/no_fstring.py`

| AST node | Reason | Substitute |
|---|---|---|
| `ast.JoinedStr` | `{...}` interpolation hides message sends and bypasses POOP `Str` | concatenation: `("Hello, " + name)`, `("count: " + str(n))` |

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

Every collection exposes `.iter()` returning a specialized one-shot iterator that mirrors Python's iterator types (`list_iterator`, `tuple_iterator`, `set_iterator`, `frozenset_iterator`, `dict_keyiterator`, `str_iterator`, `range_iterator`, `bytes_iterator`, `bytearray_iterator`, `memory_iterator`). All inherit from `_IteratorBase` (`poop/types/_iterator_base.py`), expose `.next()` and `.do(block)`, and raise `StopIteration` on exhaustion — catchable via `Try(lambda: it.next()).except_(StopIteration, handler).run()`.

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

The **protected set** is computed dynamically from `DEFAULT_NAMESPACE` (filtered to non-`_poop_*` entries) at validator instantiation time. Today: `Browser`, `Connection`, `Context`, `Cursor`, `Date`, `DateTime`, `Decimal`, `HMAC`, `Hash`, `Match`, `MimeTypes`, `Path`, `Pattern`, `PrettyPrinter`, `Random`, `Row`, `Shlex`, `Time`, `TimeDelta`, `TimeZone`, `TopologicalSorter`, `Try`, `UUID`, `With`, `binascii`, `bisect`, `copy`, `datetime`, `decimal`, `errno`, `fnmatch`, `getpass`, `glob`, `graphlib`, `hashlib`, `heapq`, `hmac`, `json`, `math`, `mimetypes`, `pprint`, `random`, `re`, `secrets`, `shlex`, `sqlite3`, `tomllib`, `uuid`, `webbrowser`. As new namespace mirrors land (`uuid`, …), they protect themselves automatically — no changes to this validator.

What the validator **does not** catch: function parameters (`def f(math): …`), lambda arguments (`lambda math: …`), and method names inside classes (`class Calc: def math(self): …`). Those bind in local scope and are typically intentional — the user knows what they're doing. The validator targets the top-level / shared-scope reassignment that surfaces as `AttributeError` much later.

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
| `ast.Subscript` | slice is not `ast.Slice` | `obj[key]` looks like an operator | `obj.at(key)` |
| `ast.Subscript` | slice is `ast.Slice` | `obj[1:3]` looks like an operator | `obj.slice(start, stop)` |

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

### Heterogeneous numeric comparisons return `false`

`Int(1) == Float(1.0)` → `false`. `Int(1) == Complex(1+0j)` → `false`. In native Python all three would be `True`.

This is intentional: POOP types are opaque to each other — an `Int` and a `Float` are distinct objects and equality is strict type identity first. The principle "every basic type has a POOP equivalent" means each type is self-contained; implicit cross-type coercion would require treating one type as subordinate to another, which breaks that symmetry.

To compare numeric values across types, convert explicitly first: `i.float() == f`, `f.int() == i`, `i.complex() == c`.

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

`With(Object)` implements the context manager protocol as a message-passing builder. The context manager block is executed lazily — only when `.do()` is called.

| Message | Method | Behavior |
|---|---|---|
| `[block] value: aResource` | `With(lambda: cm).do(lambda resource: body)` | acquires resource via `__enter__`, runs body, calls `__exit__` |

The context manager object must implement Python's `__enter__`/`__exit__` protocol — a deliberate primitive leak, consistent with `Try` using native exception types. Exceptions propagate via the standard `__exit__` return value: if `__exit__` returns falsy, the exception is re-raised; truthy suppresses it.

> **Tradeoff**: context managers must implement Python's native protocol (`__enter__`/`__exit__`). POOP cannot redefine resource acquisition semantics without reimplementing every standard context manager (files, locks, etc.), which is impractical.

`With` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/with_.py` — namespace-only, no AST rewrite.

### math — `poop/types/math.py` + `poop/transformers/math.py`

`math` is a namespace class wrapping Python's `math` module. Exposed as a namespace-only binding via the `NAMESPACE` dict in `poop/transformers/math.py` (no AST rewrite), in the same family as `Try` / `With` / `Path`. Every public callable in Python 3.14's `math` is reachable as `math.<same-name>(...)`, with parameter order, keyword-only markers, defaults, return types, **and the lowercase module name** mirroring Python exactly. The namespace binding is `math` (lowercase) because `math` is a Python module, not a class.

The five module constants follow the source module's case verbatim — `math.pi`, `math.e`, `math.tau`, `math.inf`, `math.nan` (lowercase). Other POOP namespaces inherit their own case from their source modules: `uuid.NAMESPACE_DNS`, `secrets.DEFAULT_ENTROPY`, and so on stay uppercase because that is how `uuid` and `secrets` ship them.

| Category | Operations | Returns |
|---|---|---|
| Number theory | `factorial`, `gcd(*ints)`, `lcm(*ints)`, `comb`, `perm(n, k=None)`, `isqrt` | `Int` |
| Trigonometric | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2(y, x)` | `Float` |
| Hyperbolic | `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` | `Float` |
| Exp / log / power | `exp`, `expm1`, `exp2`, `log(x, base=math.e)`, `log2`, `log10`, `log1p`, `sqrt`, `cbrt`, `pow` | `Float` |
| Rounding | `floor`, `ceil`, `trunc` | `Int` |
| Float decomposition | `modf` → `(Float, Float)`, `frexp` → `(Float, Int)`, `ldexp` | `Tuple` / `Float` |
| Angular conversion | `degrees`, `radians` | `Float` |
| Float utilities | `fabs`, `copysign`, `fmod`, `remainder`, `fma`, `ulp`, `nextafter(x, y, *, steps=None)` | `Float` |
| Predicates | `isfinite`, `isinf`, `isnan`, `isclose(a, b, *, rel_tol=1e-9, abs_tol=0.0)` | `Boolean` |
| Aggregates | `fsum`, `prod(iter, *, start=1)`, `sumprod`, `dist`, `hypot(*args)` | `Float` / `Int` |
| Special functions | `erf`, `erfc`, `gamma`, `lgamma` | `Float` |
| Constants | `pi`, `e`, `tau`, `inf`, `nan` | `Float` |

POOP `Int` and `Float` keep methods that are native to Python's `int` and `float` (`bit_length`, `bit_count`, `is_integer`, `as_integer_ratio`) and the substitutes for banned builtins (`Int.abs()`, `Int.pow()`, `Int.divmod()` cover the `no_abs` / `no_pow` / `no_divmod` validators). The math-specific public methods that previously lived on those types (`Int.ceil`/`floor`/`trunc`, `Float.ceil`/`floor`/`trunc`) are removed — `math.ceil(x)` and friends are the single source of truth.

`math` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/math.py` — namespace-only, no AST rewrite.

### cmath — `poop/types/cmath.py` + `poop/transformers/cmath.py`

`cmath` is a namespace class wrapping Python's `cmath` module — the complex-number counterpart to `math`. Same shape: namespace-only binding, lowercase `cmath`, every public name from `cmath.*` reachable as `cmath.<same-name>(...)` with matching parameter order, defaults, and return types.

Predicates (`isfinite`/`isinf`/`isnan`) take a `Complex` and return `Boolean` based on the **whole** Complex (true iff both real and imag satisfy the predicate), matching CPython's semantics. `cmath` and `math` predicates are deliberately separate (`math.isfinite(x: Float)` vs `cmath.isfinite(c: Complex)`), mirroring Python's two-namespace split.

| Category | Operations | Returns |
|---|---|---|
| Power / log | `sqrt`, `exp`, `log(x, base=None)`, `log10` | `Complex` |
| Trigonometric | `sin`, `cos`, `tan`, `asin`, `acos`, `atan` | `Complex` |
| Hyperbolic | `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` | `Complex` |
| Polar / rectangular | `phase(c)`, `polar(c)`, `rect(r, phi)` | `Float` / `Tuple(Float, Float)` / `Complex` |
| Predicates | `isfinite`, `isinf`, `isnan`, `isclose(a, b, *, rel_tol=1e-9, abs_tol=0.0)` | `Boolean` |
| Float constants | `pi`, `e`, `tau`, `inf`, `nan` | `Float` |
| Complex constants | `infj`, `nanj` | `Complex` |

`cmath` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/cmath.py` — namespace-only, no AST rewrite.

### random + Random — `poop/types/random.py` + `poop/transformers/random.py`

Python's `random` module exposes two distinct names: the lowercase `random` module (with module-level functions like `random.random()` and `random.choice(xs)`) and the PascalCase `Random` class (instantiated for seeded, independent generators: `random.Random(seed)`). POOP mirrors that split with **two namespace entries**:

- **`random`** (lowercase) — a singleton instance (`_DEFAULT = Random()`) acting as the module. Module-level entry points are calls on this singleton: `random.random()`, `random.choice(xs)`, `random.shuffle(xs)`, etc. — matching Python's `random.<func>` exactly.
- **`Random`** (PascalCase) — the class itself, callable in POOP source: `r = Random(seed); r.random()`. Equivalent to Python's `random.Random(seed)`, but shorter (POOP user code already has `Random` in scope, no `random.` prefix needed for the constructor).

This is the first POOP namespace where two names point to related but distinct objects: a module-like singleton AND its underlying class. Other module mirrors (`math`, `secrets`, `tomllib`) have only the lowercase module name because they expose no public class.

| Category | Operations | Returns |
|---|---|---|
| Bookkeeping | `seed(a=None, version=Int(2))` | `none` |
| Core draws | `random()`, `uniform(a, b)`, `randint(a, b)`, `randrange(start, stop=None, step=None)`, `getrandbits(k)`, `randbytes(n)` | `Float`/`Int`/`Bytes` |
| Collection draws | `choice(seq)`, `shuffle(x)` mutates list, returns `none`, `choices(population, weights=None, *, cum_weights=None, k=Int(1))`, `sample(population, k, *, counts=None)` | element / `none` / `List` |
| Distributions | `gauss`, `normalvariate`, `lognormvariate`, `expovariate`, `gammavariate`, `betavariate`, `paretovariate`, `weibullvariate`, `vonmisesvariate`, `triangular`, `binomialvariate` (Python 3.12+) | `Float` (10) / `Int` (binomialvariate) |

The same method set is available on both `random` (module API, uses singleton state) and on `Random(seed)` instances (independent state per instance). Anything cryptographic goes through `secrets`, not `random`.

`getstate()` answers a `RandomState` — an **opaque checkpoint token**. The CPython state tuple (version, the 625 Mersenne Twister words, the cached spare `gauss` value) stays sealed inside; the token answers equality and `setstate(state)` accepts it back, resuming the sequence mid-stream (including the `gauss()` pair cache). This mirrors the stdlib contract — "can be passed to setstate() later" — without pretending the 625 words are meaningful data. For plain reproducibility from the start, `seed(a)` remains the simpler story.

| Operation | Returns | Notes |
|---|---|---|
| `rng.getstate()` / `random.getstate()` | `RandomState` | opaque checkpoint |
| `rng.setstate(state)` / `random.setstate(state)` | `none` | resumes exactly at the checkpoint; the token transfers between generators |

`random` and `Random` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/random.py` — namespace-only, no AST rewrite.

### errno — `poop/types/errno.py` + `poop/transformers/errno.py`

`errno` is a constant-only namespace mirroring Python's `errno` module. Every integer error code Python exposes (`EPERM`, `ENOENT`, `EAGAIN`, `EWOULDBLOCK`, …) is bound on the `Errno` class as a POOP `Int` class attribute under the same uppercase name. The reverse map `errno.errorcode` is a POOP `Dict[Int, Str]` keyed by canonical code, mirroring CPython exactly (so aliases like `EAGAIN`/`EWOULDBLOCK` collapse to a single entry).

| Member | Type | Notes |
|---|---|---|
| `errno.EPERM`, `errno.ENOENT`, … (all 134 codes Python exposes) | `Int` | Same name as `errno.<NAME>` in CPython |
| `errno.errorcode` | `Dict[Int, Str]` | 131 entries — canonical names only |

The set of constants is built at import time by enumerating `dir(errno)` rather than maintained by hand, so POOP automatically tracks whichever subset CPython exposes on the host (Linux / macOS / Windows). Lowercase `errno` keeps the lowercase module-name convention; constants are uppercase because that is how CPython ships them.

`errno` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/errno.py` — namespace-only, no AST rewrite.

### getpass — `poop/types/getpass.py` + `poop/transformers/getpass.py`

`getpass` is a tiny namespace mirroring Python's `getpass` module. Both reads return POOP `Str`:

| Operation | Returns | Notes |
|---|---|---|
| `getpass.getpass(prompt=Str("Password: "), stream=none)` | `Str` | Reads without echo |
| `getpass.getuser()` | `Str` | Login name lookup |

`getpass.GetPassWarning` is **not surfaced** in POOP. CPython emits it via `warnings` when echo can't be suppressed, but POOP has no warning concept (`warnings` itself is "out" — see proposals.md). The underlying CPython call still writes the warning to stderr; POOP user code just cannot catch or filter it. See proposals.md § Future work for a possible later exposure path.

`getpass` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/getpass.py` — namespace-only, no AST rewrite.

### base64 — methods on `Bytes` and `Str`

Python's `base64.*` is reachable as **methods on the value**, not a namespace. Both `Bytes` (encode + decode) and `Str` (decode only) carry the full surface:

| Direction | Receivers | Methods |
|---|---|---|
| Encode | `Bytes` | `b16encode`, `b32encode`, `b32hexencode`, `b64encode`, `standard_b64encode`, `urlsafe_b64encode`, `a85encode`, `b85encode`, `z85encode` |
| Decode | `Bytes`, `Str` | `b16decode`, `b32decode`, `b32hexdecode`, `b64decode`, `standard_b64decode`, `urlsafe_b64decode`, `a85decode`, `b85decode`, `z85decode` |

The optional kwargs mirror the stdlib on both receivers: `b64encode(altchars)` / `b64decode(altchars, validate)`, `b16decode(casefold)`, `b32decode(casefold, map01)`, `b32hexdecode(casefold)`, `a85encode(foldspaces, wrapcol, pad, adobe)` / `a85decode(foldspaces, adobe, ignorechars)`, `b85encode(pad)` — on `Str` receivers the `Str`-typed kwargs (`altchars`, `map01`, `ignorechars`) are accepted as `Str` and coerced. Encoders return `Bytes` (ASCII-bearing), mirroring `base64.<name>(b)` in Python — callers wanting a textual `Str` must explicitly `.decode(Str("ascii"))` afterward, exactly as in Python. Decoders also return `Bytes`.

No new POOP type, no transformer, no AST rewrite — the methods live directly on the existing `Bytes` and `Str` classes.

### secrets — `poop/types/secrets.py` + `poop/transformers/secrets.py`

`secrets` is a cryptographic-secure-only namespace mirroring Python's `secrets` module. POOP deliberately separates secure (`secrets`) from non-secure (`random`) randomness to match Python's API split exactly.

| Category | Operations | Returns |
|---|---|---|
| Token minting | `token_bytes(nbytes=none)`, `token_hex(nbytes=none)`, `token_urlsafe(nbytes=none)` | `Bytes` / `Str` / `Str` |
| Secure draws | `choice(seq)`, `randbelow(exclusive_upper_bound)`, `randbits(k)` | element / `Int` / `Int` |
| Constant-time comparison | `compare_digest(a, b, /)` (positional-only) | `Boolean` |
| Constant | `DEFAULT_ENTROPY` | `Int` (32 in CPython) |

`secrets.SystemRandom` is **not** surfaced — its instance API duplicates the module-level functions above. `nbytes=none` resolves to `DEFAULT_ENTROPY`, mirroring CPython's default.

`secrets` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/secrets.py` — namespace-only, no AST rewrite.

### binascii — `poop/types/binascii.py` + `poop/transformers/binascii.py`

`binascii` mirrors Python's `binascii` module — lower-level one-shot conversions between binary data and ASCII representations, plus CRC checksums. Pairs with `base64` (the methods on `Bytes`/`Str`).

| Category | Operations | Returns |
|---|---|---|
| Hex | `b2a_hex(data, sep=none, bytes_per_sep=Int(1))`, `hexlify(...)` (alias), `a2b_hex(hexstr)`, `unhexlify(hexstr)` (alias) | `Bytes` |
| Base64 / qp / uu (one-shot) | `b2a_base64(data)`, `a2b_base64(data)`, `b2a_qp(data)`, `a2b_qp(data)`, `b2a_uu(data)`, `a2b_uu(data)` | `Bytes` |
| CRC | `crc_hqx(data, value)`, `crc32(data, value=Int(0))` | `Int` |
| Exception classes | `binascii.Error`, `binascii.Incomplete` | Python exception types |

The two exception classes are exposed as raw Python types so user code can pass them to `Try.except_(...)`. Exception classes are the documented exception to POOP's type-discipline rule — `Try` already accepts a Python exception type for its handler, so exposing these mirrors that existing convention.

`b2a_hqx`/`a2b_hqx` (Mac BinHex 4) are not exposed because Python removed them in 3.13.

`binascii` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/binascii.py` — namespace-only, no AST rewrite.

### mimetypes + MimeTypes — `poop/types/mimetypes.py` + `poop/transformers/mimetypes.py`

`mimetypes` mirrors Python's `mimetypes` module — extension/MIME-type lookups. Like `random`/`Random`, POOP exposes **two namespace entries** because the source module ships both a module-level API and a reusable class:

- **`mimetypes`** (lowercase) — module-level shortcuts plus the standard registry constants. Operates on CPython's process-global registry.
- **`MimeTypes`** (PascalCase) — the reusable registry class. `MimeTypes(filenames=List, strict=Boolean)` builds an isolated instance with its own state.

| Category | Operations | Returns |
|---|---|---|
| Lookups | `guess_type(url, strict=true)`, `guess_extension(type, strict=true)`, `guess_all_extensions(type, strict=true)` | `Tuple[Str/none, Str/none]` / `Str | none` / `List[Str]` |
| Mutation | `add_type(type, ext, strict=true)`, `init(files=none)`, `read_mime_types(filename)` (module-only) | `none` / `none` / `Dict | none` |
| Constants (module-only) | `suffix_map`, `encodings_map`, `types_map`, `common_types` (all `Dict[Str, Str]`), `knownfiles` (`List[Str]`) | snapshot at import time |

The constant dicts are **snapshotted** from CPython's globals at import time. Subsequent `add_type` calls update CPython's mutable globals but not the POOP snapshots — this preserves POOP's "no introspection" stance: constants are immutable values from POOP's perspective. Use `MimeTypes` if you need a registry that reflects later mutations.

`mimetypes` and `MimeTypes` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/mimetypes.py` — namespace-only, no AST rewrite.

### webbrowser + Browser — `poop/types/webbrowser.py` + `poop/transformers/webbrowser.py`

`webbrowser` mirrors Python's `webbrowser` module — open URLs in the user's default (or a chosen) browser. Like `random`/`Random` and `mimetypes`/`MimeTypes`, two namespace entries are bound:

- **`webbrowser`** (lowercase) — module-level shortcuts and the `get(using=none)` factory.
- **`Browser`** (PascalCase) — wraps the underlying `webbrowser.BaseBrowser` controller returned by `get()`, exposing the same `open`/`open_new`/`open_new_tab` methods.

| Operation | Returns | Notes |
|---|---|---|
| `webbrowser.open(url, new=Int(0), autoraise=true)` | `Boolean` | True iff a browser launched successfully |
| `webbrowser.open_new(url)` | `Boolean` | new window |
| `webbrowser.open_new_tab(url)` | `Boolean` | new tab |
| `webbrowser.get(using=none)` | `Browser` | controller; raises `webbrowser.Error` if `using` unknown |
| `webbrowser.Error` | Python type | usable with `Try.except_` |
| `Browser.open` / `.open_new` / `.open_new_tab` | `Boolean` | per-instance dispatch |
| `Browser.name` | `Str` | controller name (e.g. `"chrome"`) |

POOP collapses Python's concrete browser classes (Chrome, Edge, Mozilla, …) into a single `Browser` POOP type because every concrete class carries the same public surface. Class identity is preserved internally for dispatch.

`webbrowser.register(name, constructor=none, instance=none, *, preferred=false)` accepts a POOP `Block` for `constructor`. The block runs through `block.bridge` and must return a `Browser` (or a raw `BaseBrowser`) — the registry layer unwraps to `BaseBrowser` for CPython.

`webbrowser` and `Browser` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/webbrowser.py` — namespace-only, no AST rewrite.

### glob — `poop/types/glob.py` + `poop/transformers/glob.py`

`glob` mirrors Python's `glob` module — shell-style wildcard expansion driven from a string pattern. `Path.glob`/`Path.rglob` cover most use; this namespace surfaces the module-level entry points for callers who want to glob without first constructing a `Path`.

| Operation | Returns | Notes |
|---|---|---|
| `glob.glob(pathname, *, root_dir=none, recursive=false, include_hidden=false)` | `List[Path]` | eager |
| `glob.iglob(pathname, *, root_dir=none, recursive=false, include_hidden=false)` | `GlobIter` | lazy; iterable, with `.to_list()` |
| `glob.escape(pathname)` | `Str` | escapes glob metacharacters |
| `glob.translate(pat, *, recursive=false, include_hidden=false, seps=none)` | `Str` | compiles the pattern to a regex source string (3.13+) |

`GlobIter` wraps Python's `iglob` generator and yields POOP `Path` instances. The `dir_fd` parameter on CPython's `glob.glob` is not surfaced — POOP routes file-descriptor-based I/O nowhere yet.

`glob` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/glob.py` — namespace-only, no AST rewrite.

### fnmatch — `poop/types/fnmatch.py` + `poop/transformers/fnmatch.py`

`fnmatch` mirrors Python's `fnmatch` module — Unix shell-pattern matching against filenames.

| Operation | Returns |
|---|---|
| `fnmatch.fnmatch(filename, pattern)` | `Boolean` (case rules follow the OS) |
| `fnmatch.fnmatchcase(filename, pattern)` | `Boolean` (always case-sensitive) |
| `fnmatch.filter(names, pattern)` | `List[Str]` |
| `fnmatch.translate(pattern)` | `Str` (regex source) |

`fnmatch` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/fnmatch.py` — namespace-only, no AST rewrite.

### copy — `poop/types/copy.py` + `poop/transformers/copy.py`

`copy` mirrors Python's `copy` module — shallow and deep object copying. POOP types implement `__copy__` / `__deepcopy__` via the standard Python protocol; the namespace just routes calls.

| Operation | Returns | Notes |
|---|---|---|
| `copy.copy(obj)` | same type as input | shallow |
| `copy.deepcopy(obj)` | same type as input | recursive |
| `copy.Error` | Python exception type | usable with `Try.except_` |

`deepcopy`'s `memo` parameter (an `id(obj)`-keyed dict CPython uses to track recursive identities during traversal) is **not** surfaced — it has no clean type-discipline mapping because POOP `Dict` is keyed by POOP `Object`, not `int`. Callers wanting custom memoization should implement `__deepcopy__` on their POOP class. `copy.replace` (3.13+) is similarly out of scope for v1 — POOP classes don't use decorators and have no `dataclasses` story.

`copy` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/copy.py` — namespace-only, no AST rewrite.

### pprint + PrettyPrinter — `poop/types/pprint.py` + `poop/transformers/pprint.py`

`pprint` mirrors Python's `pprint` module — multi-line, indented printing of nested data structures. POOP types alias `__repr__` to `__str__`, so pretty-printed output reads naturally for POOP values.

Two namespace entries follow the `random`/`Random` and `mimetypes`/`MimeTypes` convention:

- **`pprint`** (lowercase) — module-level shortcuts.
- **`PrettyPrinter`** (PascalCase) — reusable printer with knobs.

| Operation | Returns | Notes |
|---|---|---|
| `pprint.pprint(obj, *, indent, width, depth, compact, sort_dicts, underscore_numbers)` | `none` | writes to stdout |
| `pprint.pformat(obj, *, …)` | `Str` | returns the formatted string |
| `pprint.pp(obj, *, …)` | `none` | like `pprint`, default `sort_dicts=false` |
| `pprint.isreadable(obj)` | `Boolean` | output is eval-friendly? |
| `pprint.isrecursive(obj)` | `Boolean` | object contains self-references? |
| `pprint.saferepr(obj)` | `Str` | safe repr that doesn't recurse |
| `PrettyPrinter(indent, width, depth, *, compact, sort_dicts, underscore_numbers)` | `PrettyPrinter` | reusable instance with `.pprint`/`.pformat`/`.isreadable`/`.isrecursive` |

`PrettyPrinter` captures `sys.stdout` at construction time, matching CPython exactly — building one inside a stream redirect is the way to capture output.

`pprint` and `PrettyPrinter` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/pprint.py` — namespace-only, no AST rewrite.

### bisect — `poop/types/bisect.py` + `poop/transformers/bisect.py`

`bisect` mirrors Python's `bisect` module — binary search and ordered insertion on sorted POOP `List`s. No new POOP type; the operations all take a `List`.

| Operation | Returns | Notes |
|---|---|---|
| `bisect.bisect_left(a, x, lo=none, hi=none, *, key=none)` | `Int` | leftmost insertion point |
| `bisect.bisect_right(a, x, lo=none, hi=none, *, key=none)` | `Int` | rightmost insertion point |
| `bisect.bisect(a, x, …)` | `Int` | alias for `bisect_right` |
| `bisect.insort_left(a, x, …)` | `none` | mutates `a` in place |
| `bisect.insort_right(a, x, …)` | `none` | mutates `a` in place |
| `bisect.insort(a, x, …)` | `none` | alias for `insort_right` |

`key` is a Python callable applied to elements during comparison; insertion mutators follow POOP's mutator convention (return `none`).

`bisect` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/bisect.py` — namespace-only, no AST rewrite.

### heapq — `poop/types/heapq.py` + `poop/transformers/heapq.py`

`heapq` mirrors Python's `heapq` module — a binary min-heap on a regular POOP `List`. No new POOP type for the heap itself; operations mutate the underlying buffer.

| Operation | Returns | Notes |
|---|---|---|
| `heapq.heappush(heap, item)` | `none` | in-place |
| `heapq.heappop(heap)` | element | raises `IndexError` on empty |
| `heapq.heappushpop(heap, item)` | element | one-step push+pop |
| `heapq.heapreplace(heap, item)` | element | one-step pop+push |
| `heapq.heapify(x)` | `none` | in-place rearrangement |
| `heapq.nlargest(n, iterable, key=none)` | `List` | sorted descending |
| `heapq.nsmallest(n, iterable, key=none)` | `List` | sorted ascending |
| `heapq.merge(*iterables, key=none, reverse=false)` | `HeapMerge` | lazy iterator with `.to_list()` |

Private max-heap variants (`_heapify_max`, etc.) are intentionally out of scope.

`heapq` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/heapq.py` — namespace-only, no AST rewrite.

### collections + Counter + Deque — `poop/types/collections.py` + `poop/transformers/collections.py`

`collections` mirrors Python's `collections` module — the Smalltalk-flavoured data structures. Seven namespace entries: `collections` (lowercase module mirror), plus the direct entry points `Counter`, `deque`, `defaultdict`, `OrderedDict`, `ChainMap`, and `namedtuple` — each keeping its Python casing (`deque`/`defaultdict`/`namedtuple` are lowercase in CPython, same precedent as enum's `auto`). Elements live inside the impl containers as POOP objects — they hash and compare like the Python values they masquerade as. `defaultdict` and `OrderedDict` subclass `Dict`, so the full `Dict` surface (`at_put`, `keys`, `do`, `pop`, views, `|` merge, …) applies.

| Operation | Returns | Notes |
|---|---|---|
| `Counter(source=none)` | `Counter` | from iterable, `Dict` of counts, or another `Counter`; Smalltalk's `Bag` |
| `Counter.at(key)` | `Int` | missing keys answer `0`, never raise |
| `Counter.at_put(key, count)` | `Counter` | sets the count, returns self |
| `Counter.most_common(n=none)` | `List[Tuple]` | `(element, Int)` pairs, descending count |
| `Counter.elements()` | `List` | each element repeated by its count |
| `Counter.total()` | `Int` | sum of all counts |
| `Counter.update(source)` / `.subtract(source)` | `none` | add / subtract counts; `none` is a no-op |
| `Counter.len()` / `.includes(key)` | `Int` / `Boolean` | distinct elements / membership |
| `Counter.do(block)` | `none` | block receives `(element, count)` `Tuple`s, mirroring `Dict.do` |
| `c1 + c2` / `c1 - c2` / `c1 & c2` / `c1 \| c2` | `Counter` | merge / saturating subtract / min / max; isinstance-guarded |
| `deque(source=none, maxlen=none)` | `deque` | Smalltalk's `OrderedCollection`; bounded when `maxlen` given |
| `deque.append(x)` / `.appendleft(x)` | `none` | O(1) at both ends |
| `deque.pop()` / `.popleft()` | element | raises `IndexError` on empty |
| `deque.extend(iter)` / `.extendleft(iter)` | `none` | `extendleft` reverses, like the stdlib |
| `deque.rotate(n=1)` | `none` | negative rotates left |
| `deque.count(x)` / `.remove(x)` / `.reverse()` / `.clear()` | `Int` / `none` | |
| `deque.insert(i, x)` / `.index(x, start=none, stop=none)` | `none` / `Int` | `index` raises `ValueError` when absent |
| `deque.copy()` | `deque` | preserves `maxlen` |
| `d1 + d2` / `d * n` | `deque` | concatenation / repetition; isinstance-guarded |
| `deque.at(i)` | element | negative indexing supported |
| `deque.maxlen` (property) | `Int` or `none` | |
| `deque.len()` / `.includes(x)` | `Int` / `Boolean` | |
| `deque.do/map/filter/...` | typed | full `_IterableMixin` surface |
| `defaultdict(default_factory=none, source=none)` | `defaultdict` | factory is a block (`lambda: List()`); `at` on a missing key calls it, stores, and answers — no `KeyError`; optional `Dict` source seeds the contents |
| `defaultdict.default_factory` (property) | block or `none` | |
| `defaultdict.<Dict surface>` | typed | inherits everything from `Dict` |
| `OrderedDict(source=none)` | `OrderedDict` | order-aware `Dict`; optional `Dict` source seeds the contents |
| `OrderedDict.move_to_end(key, last=true)` | `none` | `last=false` moves to front |
| `OrderedDict.popitem(last=true)` | `Tuple` | directional pop |
| `OrderedDict.<Dict surface>` | typed | inherits everything from `Dict` |
| `ChainMap(*maps)` | `ChainMap` | lookup chain over `Dict`s (subclasses welcome); empty call seeds one empty `Dict`; live over the underlying maps |
| `ChainMap.at(key)` / `.get(key, default=none)` | value | searches each map in order |
| `ChainMap.at_put(key, val)` | `ChainMap` | writes land on the first map; returns self |
| `ChainMap.includes(key)` / `.len()` | `Boolean` / `Int` | deduplicated across maps |
| `ChainMap.do(block)` | `none` | `(key, value)` pairs, mirroring `Dict.do` |
| `ChainMap.maps` (property) | `List[Dict]` | the chain, first map first |
| `ChainMap.new_child(m=none)` / `.parents` (property) | `ChainMap` | prepend a map / drop the first |
| `namedtuple(typename, field_names)` | class | class factory: fields as a `Str` (`"x y"` / `"x, y"`) or iterable of `Str` |
| `Point(...)` (generated class) | instance | a `Tuple` subclass — fields read as properties (`p.x`), arity-checked constructor, `Point(x=1, y=2)`-style repr |
| `Point._fields` (class attr) | `Tuple[Str]` | field names, Python's underscore convention kept verbatim |
| `Point._make(iterable)` | instance | classmethod, builds from an iterable |
| `p._asdict()` | `Dict` | `Str` field names → values |
| `p._replace(**changes)` | instance | new value with named fields swapped; unknown names raise `ValueError` |

### functools + partial — `poop/types/functools.py` + `poop/transformers/functools.py`

`functools` mirrors Python's `functools` module. Two namespace entries: `functools` (lowercase module mirror) and `partial` (direct entry point — lowercase, matching CPython's casing like collections' `deque`). `reduce` already lives on every iterable as `col.reduce(init, block)` — the module mirror exists for parity. Caching arrives as **explicit wrapper calls on blocks**, not decorators, so no decorator story is required.

| Operation | Returns | Notes |
|---|---|---|
| `partial(block, *args, **kwargs)` | `partial` | freezes arguments of **any** callable — a block, a bound method (`account.deposit`), a constructor, another `partial`; frozen values stay POOP objects |
| `partial(...)(*more)` | value | call-transparent; call-site kwargs override frozen ones |
| `partial.func` / `.args` / `.keywords` (properties) | callable / `Tuple` / `Dict` | mirror the stdlib triple |
| `functools.cmp_to_key(block)` | `Block` | block receives two values and answers a negative/zero/positive `Int`; feed the result to the `key=` of the sorting messages |
| `functools.reduce(block, iterable, init=none)` | value | `none` init means absent, like the stdlib two-arg form; `col.reduce(init, block)` is the idiomatic message |
| `functools.cache(block)` | memoized `Block` | `quadrado = functools.cache(lambda n: n * n)`; arguments must be hashable (Int/Str/Tuple are; List/Dict are not — same rule as Python) |
| `functools.lru_cache(block, maxsize=none)` | memoized `Block` | bounded memoization; `none` maxsize means unbounded |
| `<memoized>.cache_info()` | `Dict` | `hits`/`misses`/`maxsize`/`currsize` as `Int` (`maxsize` is `none` when unbounded) |
| `<memoized>.cache_clear()` | `none` | resets the cache |
| `functools.partialmethod(method, *args, **kwargs)` | descriptor | assign in a class body (`deposit_100 = functools.partialmethod(deposit, 100)`); binds like the stdlib |

`wraps`, `singledispatch`, and `total_ordering` stay out: the first two are machinery for writing decorators (POOP has no user decorators) and `singledispatch` is type dispatch — polymorphism's job.

### shlex + Shlex — `poop/types/shlex.py` + `poop/transformers/shlex.py`

`shlex` mirrors Python's `shlex` module — POSIX-style shell tokenization, joining, and safe quoting. Two namespace entries follow the `random`/`Random` convention:

- **`shlex`** (lowercase) — module-level `split`/`join`/`quote`.
- **`Shlex`** (PascalCase) — the streaming lexer class, mirrors `shlex.shlex`.

| Operation | Returns | Notes |
|---|---|---|
| `shlex.split(s, comments=false, posix=true)` | `List[Str]` | POSIX-style tokenization |
| `shlex.join(split_command)` | `Str` | safely re-joins a list of args |
| `shlex.quote(s)` | `Str` | shell-safe escape for one token |
| `Shlex(instream=none, infile=none, posix=false, punctuation_chars=false)` | `Shlex` | streaming lexer |
| `Shlex.get_token()` | `Str | none` | next token; `none` signals EOF |
| iterating a `Shlex` | yields `Str` | wraps CPython's iter protocol |
| `Shlex.lineno` (property) | `int` | source line counter |
| `Shlex.whitespace_split` (property) | `bool` | configurable splitting mode |

The lexer API is covered: `get_token`/`read_token`/`push_token`, `push_source`/`pop_source`, `error_leader`, `lineno`, and the character-class attributes (`commenters`, `wordchars`, `whitespace`, `escape`, `quotes`, `escapedquotes`, `whitespace_split`, `debug`, `token`, `infile`, `source`, `punctuation_chars`). The remainder is out by design, not deferred: `eof` (POOP answers `none` at end of input instead of a sentinel), `sourcehook` (returns an open file object — POOP has no file-object abstraction, same family as `ZoneInfo.from_file`), and `instream`/`state`/`pushback`/`filestack` (parser internals; exposing them breaks encapsulation).

`shlex` and `Shlex` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/shlex.py` — namespace-only, no AST rewrite.

### uuid + UUID — `poop/types/uuid.py` + `poop/transformers/uuid.py`

`UUID` is a full POOP value wrapping `uuid.UUID`. Construction mirrors CPython exactly — positional `UUID(Str("12345...-…"))` for a canonical string or keyword `UUID(hex=..., bytes=..., bytes_le=..., int=..., fields=...)` for the parse-from-foo variants. Like `random`/`Random` and `mimetypes`/`MimeTypes`, two namespace entries are bound:

- **`uuid`** (lowercase) — module-level generators, helpers, and constants.
- **`UUID`** (PascalCase) — the class.

| Category | Members | Returns |
|---|---|---|
| Representations | `.hex`, `.urn` (`Str`), `.int` (`Int`), `.bytes`, `.bytes_le` (`Bytes`), `.fields` (`Tuple[Int x 6]`) | per row |
| Field accessors | `.time_low`, `.time_mid`, `.time_hi_version`, `.clock_seq_hi_variant`, `.clock_seq_low`, `.node`, `.time`, `.clock_seq` | `Int` |
| Classification | `.version` (`Int`), `.variant` (`Str`), `.is_safe` (`Str` token: `"safe"`/`"unsafe"`/`"unknown"`) | per row |
| Generators | `uuid.uuid1`/`3`/`4`/`5`/`6`/`7`/`8` | `UUID` |
| Helper | `uuid.getnode()` | `Int` |
| Namespace constants (`UUID`) | `uuid.NAMESPACE_DNS`/`URL`/`OID`/`X500`, `uuid.NIL`, `uuid.MAX` | `UUID` |
| Variant constants (`Str`) | `uuid.RESERVED_NCS`, `uuid.RFC_4122`, `uuid.RESERVED_MICROSOFT`, `uuid.RESERVED_FUTURE` | `Str` |

**`is_safe` divergence.** CPython returns a `SafeUUID` enum. POOP flattens to a lowercase `Str` token (`"safe"` / `"unsafe"` / `"unknown"`) to avoid introducing a one-off enum type — sanctioned divergence, called out in the proposal.

`uuid.SafeUUID` is not exposed as a dedicated POOP enum (see above). `uuid.uuid6`/`7`/`8` are new in Python 3.14 and surfaced unchanged.

`uuid` and `UUID` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/uuid.py` — namespace-only, no AST rewrite.

### json — `poop/types/json.py` + `poop/transformers/json.py`

`json` mirrors Python's `json` module — (de)serialisation between JSON text and POOP value graphs.

| Operation | Returns | Notes |
|---|---|---|
| `json.dumps(obj, *, skipkeys, ensure_ascii, check_circular, allow_nan, indent, sort_keys)` | `Str` | full POOP value tree → JSON |
| `json.loads(s)` | POOP value | JSON → full POOP value tree |
| `json.dump(obj, path, …)` | `none` | path-based serialise (POOP I/O convention) |
| `json.load(path)` | POOP value | path-based deserialise |
| `json.JSONDecodeError` | Python exception type | usable with `Try.except_` |

**Round-trip type discipline.** The native `json` library walks Python types; this namespace wraps every entry/exit with `_unwrap`/`_wrap` so callers never see a raw `dict`/`list`/`str`/`int`/`float`/`bool`/`None`. `Json.loads('{"a":1, "b":true}')` returns a `Dict[Str, Int | Boolean]` — every value is a POOP type. `Json.dumps(d)` accepts a POOP value graph and returns POOP `Str`.

The full surface is covered: subclassing (`JSONEncoder` with a bridged `default` override via `__init_subclass__`; `JSONDecoder` taking the hook kwargs as blocks) and the callback kwargs on `dumps`/`loads`/`dump`/`load` (`cls`, `default`, `object_hook`, `parse_int`/`parse_float`/`parse_constant`, `object_pairs_hook`, `separators`) — all blocks route through `block.bridge`, so they receive and return POOP values. Only `json.tool` (CLI) stays out of scope.

`json` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/json.py` — namespace-only, no AST rewrite.

### tomllib — `poop/types/tomllib.py` + `poop/transformers/tomllib.py`

`tomllib` mirrors Python's `tomllib` (3.11+) — read-only TOML parsing for `pyproject.toml`, ruff/ty configs, and other modern Python config formats.

| Operation | Returns | Notes |
|---|---|---|
| `tomllib.loads(s, /, *, parse_float=float)` | `Dict[Str, …]` | from `Str`; `parse_float` accepts a POOP `Block` routed through `block.bridge` |
| `tomllib.load(path, /, *, parse_float=float)` | `Dict[Str, …]` | from POOP `Path` — receiver-type divergence: CPython takes a binary file, POOP has no file-object abstraction |
| `tomllib.TOMLDecodeError` | Python exception type | usable with `Try.except_` |

TOML date / time / datetime values land as POOP `Date` / `Time` / `DateTime`. Write support stays out of scope (`tomllib` is read-only upstream).

`tomllib` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/tomllib.py` — namespace-only, no AST rewrite.

### hmac + HMAC — `poop/types/hmac.py` + `poop/transformers/hmac.py`

`hmac` mirrors Python's `hmac` module — RFC 2104 keyed-hash MAC. Pairs with `hashlib` (still proposed).

| Operation | Returns | Notes |
|---|---|---|
| `hmac.new(key, msg=none, digestmod=Str("sha256"))` | `HMAC` | digestmod accepts CPython's string form |
| `hmac.digest(key, msg, digest)` | `Bytes` | one-shot, constant-time-friendly |
| `hmac.compare_digest(a, b, /)` | `Boolean` | delegates to CPython |
| `HMAC.update(msg)` | `none` | mutates in place |
| `HMAC.digest()` | `Bytes` | |
| `HMAC.hexdigest()` | `Str` | |
| `HMAC.copy()` | `HMAC` | independent clone |
| `HMAC.digest_size` / `.block_size` (property) | `Int` | |
| `HMAC.name` (property) | `Str` | e.g. `"hmac-sha256"` |

Until `hashlib` ships, `digestmod` is typed as `Str` (mirroring CPython's string-name form). When `hashlib` lands, the type widens to also accept hash constructors.

`hmac` and `HMAC` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/hmac.py` — namespace-only, no AST rewrite.

### graphlib + TopologicalSorter — `poop/types/graphlib.py` + `poop/transformers/graphlib.py`

`graphlib` mirrors Python's `graphlib` (3.9+) — topological sorting of node graphs for dependency resolution.

| Operation | Returns | Notes |
|---|---|---|
| `TopologicalSorter(graph=none)` | `TopologicalSorter` | `graph` is `Dict[node, Iterable[predecessors]]` |
| `.add(node, *predecessors)` | `none` | incremental build |
| `.prepare()` | `none` | finalize, lock structure |
| `.is_active()` | `Boolean` | any nodes left to consume? |
| `.get_ready()` | `Tuple[node]` | nodes whose predecessors are done |
| `.done(*nodes)` | `none` | mark nodes consumed |
| `.static_order()` | `Tuple[node]` | one-shot full sort |
| `graphlib.CycleError` | Python exception type | usable with `Try.except_` |

`graphlib` and `TopologicalSorter` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/graphlib.py` — namespace-only, no AST rewrite.

### sqlite3 + Connection + Cursor + Row — `poop/types/sqlite3.py` + `poop/transformers/sqlite3.py`

`sqlite3` mirrors Python's `sqlite3` module — the stdlib's zero-config relational store. Three wrapper classes (`Connection`, `Cursor`, `Row`) cover the cursor-iteration model.

| Operation | Returns | Notes |
|---|---|---|
| `sqlite3.connect(database, timeout=none, detect_types=none, isolation_level=none, check_same_thread=none, cached_statements=none, uri=none)` | `Connection` | `database` is a `Str` or POOP `Path` |
| `sqlite3.sqlite_version` (class attr) | `Str` | SQLite library version |
| `sqlite3.PARSE_DECLTYPES` / `PARSE_COLNAMES` (class attrs) | `Int` | type-detection flags |
| `sqlite3.Warning` / `Error` / `InterfaceError` / `DatabaseError` / `DataError` / `OperationalError` / `IntegrityError` / `InternalError` / `ProgrammingError` / `NotSupportedError` | Python exception types | usable with `Try.except_` |
| `sqlite3.Connection` / `Cursor` / `Row` / `Blob` (class attrs) | `type[…]` | wrapper classes |
| `Connection.cursor()` | `Cursor` | |
| `Connection.commit()` / `.rollback()` / `.close()` / `.interrupt()` | `none` | |
| `Connection.execute(sql, params=none)` | `Cursor` | shortcut: open cursor + execute |
| `Connection.executemany(sql, seq)` | `Cursor` | `seq` is a POOP `List` / `Tuple` of param tuples |
| `Connection.executescript(script)` | `Cursor` | multi-statement script |
| `Connection.iterdump()` | `List[Str]` | SQL dump as lines |
| `Connection.backup(target, pages=none, name=none, sleep=none)` | `none` | online backup |
| `Connection` as context manager (`with`) | `Connection` | commit on success, rollback on exception |
| `Cursor.execute` / `.executemany` / `.executescript` | `Cursor` | self-returning for chaining |
| `Cursor.fetchone()` | `Tuple \| NoneClass` | |
| `Cursor.fetchmany(size=none)` | `List[Tuple]` | |
| `Cursor.fetchall()` | `List[Tuple]` | |
| `Cursor.close()` | `none` | |
| `Cursor.rowcount` / `.lastrowid` / `.arraysize` (properties) | `Int` (`lastrowid` may be `NoneClass`) | |
| `Cursor.description` (property) | `Tuple \| NoneClass` | tuple of column descriptions |
| `Cursor` is iterable | yields `Tuple` per row | streaming consumption |
| `Row(columns, values)` | `Row` | dict-like row access |
| `Row.at(index_or_name)` | wrapped value | `Int` index or `Str` column name |
| `Row.keys()` / `.values()` | `Tuple` | |
| `Row.len()` | `Int` | |
| `Connection.create_function(name, narg, func, *, deterministic=false)` | `none` | `func` is a `Block` routed through `block.bridge` |
| `Connection.create_collation(name, callable_)` | `none` | `callable_` is a `Block` routed through the bridge; pass `None` to deregister |
| `Connection.create_aggregate(name, n_arg, aggregate_class)` | `none` | `aggregate_class` is a regular POOP class with `step(*args)` / `finalize()` methods. `step` receives POOP-wrapped column values; `finalize` returns a POOP value that POOP unwraps to a SQL-storable primitive |
| `sqlite3.register_adapter(type_, adapter)` | `none` | `adapter` is a `Block` that converts the registered type to a SQL-storable value |
| `sqlite3.register_converter(typename, converter)` | `none` | `converter` is a `Block` that decodes the raw `Bytes` payload for column type `typename` |
| `sqlite3.complete_statement(sql)` | `Boolean` | true when `sql` is a complete SQLite statement |
| `sqlite3.enable_callback_tracebacks(flag)` | `none` | toggle tracebacks for errors in user-defined SQL callbacks |
| `Connection.blobopen(table, column, row, *, readonly=false, name=none)` | `Blob` | open a Blob for random-access I/O |
| `Blob.read(length=none)` / `.write(data)` / `.tell()` / `.seek(offset, origin=none)` / `.length()` / `.close()` | `Bytes` / `none` / `Int` / `none` / `Int` / `none` | random-access blob I/O; supports `with` |

Value wrapping: SQLite values are wrapped back to POOP on the way out (`int`→`Int`, `float`→`Float`, `str`→`Str`, `bytes`→`Bytes`, `None`→`none`). Bound parameters are unwrapped on the way in (POOP `Tuple`/`List` of POOP values → Python tuple of raw values).

`sqlite3.complete_statement` and `sqlite3.enable_callback_tracebacks` are out of scope (debug/shell helpers).

`sqlite3`, `Connection`, `Cursor`, and `Row` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/sqlite3.py` — namespace-only, no AST rewrite.

### decimal + Decimal + Context — `poop/types/decimal.py` + `poop/transformers/decimal.py`

`decimal` mirrors Python's `decimal` module — arbitrary-precision decimal arithmetic (money, accounting, anything where binary-float rounding error is unacceptable). `Decimal` is the number; `Context` carries precision, rounding mode, traps and flags.

| Operation | Returns | Notes |
|---|---|---|
| `Decimal(value)` | `Decimal` | `value` is `Int`, `Float`, `Str`, `Tuple(sign, digits, exponent)`, or `Decimal` |
| `Decimal + / - / * / / / // / % / ** Decimal` | `Decimal` | full arithmetic surface |
| `-Decimal` / `+Decimal` / `abs(Decimal)` | `Decimal` | unary |
| `Decimal < / <= / > / >= Decimal` | `Boolean` | |
| `.quantize(exp, rounding=none)` | `Decimal` | round to a target exponent |
| `.normalize()` / `.adjusted()` | `Decimal` / `Int` | |
| `.as_tuple()` / `.as_integer_ratio()` | `Tuple` | |
| `.is_finite()` / `.is_infinite()` / `.is_nan()` / `.is_signed()` / `.is_zero()` | `Boolean` | predicates |
| `.sqrt()` / `.ln()` / `.log10()` / `.exp()` | `Decimal` | transcendentals |
| `.to_integral_value(rounding=none)` | `Decimal` | |
| `.copy_abs()` / `.copy_negate()` / `.compare(other)` | `Decimal` | |
| `decimal.Decimal` (class attr) | `type[Decimal]` | |
| `decimal.ROUND_UP/DOWN/HALF_UP/HALF_DOWN/HALF_EVEN/CEILING/FLOOR/05UP` | `Str` | rounding constants |
| `decimal.InvalidOperation` / `DivisionByZero` / `Overflow` / `Underflow` / `Inexact` / `Rounded` / `Subnormal` / `Clamped` / `FloatOperation` / `DecimalException` | Python exception types | usable with `Try.except_` |
| `decimal.getcontext()` | `Context` | |
| `decimal.setcontext(ctx)` | `none` | |
| `decimal.localcontext(ctx=none)` | context manager | use with `With` |
| `Context.prec` / `.rounding` (properties) | `Int` / `Str` | |
| `Context.create_decimal(value)` | `Decimal` | builds a Decimal under this context |

`decimal`, `Decimal`, and `Context` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/decimal.py` — namespace-only, no AST rewrite.

### datetime + Date + Time + DateTime + TimeDelta + TimeZone — `poop/types/datetime.py` + `poop/transformers/datetime.py`

`datetime` mirrors Python's `datetime` module — the canonical date, time, datetime, duration, and fixed-offset timezone types. All five wrapper classes are bound at module scope (`Date`, `Time`, …) and also accessible as `datetime.date`, `datetime.time`, etc. (the latter mirroring CPython's module attributes).

| Operation | Returns | Notes |
|---|---|---|
| `Date(year, month, day)` | `Date` | |
| `Date.today()` / `.fromisoformat(s)` / `.fromtimestamp(t)` / `.fromordinal(n)` | `Date` | constructors |
| `Date.year` / `.month` / `.day` (properties) | `Int` | |
| `Date.weekday()` / `.isoweekday()` / `.toordinal()` | `Int` | |
| `Date.isoformat()` / `.strftime(fmt)` | `Str` | |
| `Date.replace(year=none, month=none, day=none)` | `Date` | |
| `Date + TimeDelta` | `Date` | |
| `Date - TimeDelta` | `Date` | |
| `Date - Date` | `TimeDelta` | |
| `Time(hour=none, minute=none, second=none, microsecond=none, tzinfo=none)` | `Time` | |
| `Time.fromisoformat(s)` | `Time` | |
| `Time.hour` / `.minute` / `.second` / `.microsecond` (properties) | `Int` | |
| `Time.tzinfo` (property) | `TimeZone \| NoneClass` | |
| `Time.isoformat()` / `.strftime(fmt)` | `Str` | |
| `Time.replace(...)` | `Time` | |
| `DateTime(year, month, day, hour=none, ..., tzinfo=none)` | `DateTime` | |
| `DateTime.now(tz=none)` / `.utcnow()` / `.fromtimestamp(t, tz=none)` / `.fromisoformat(s)` / `.combine(date, time, tzinfo=none)` | `DateTime` | constructors |
| `DateTime.date()` / `.time()` | `Date` / `Time` | |
| `DateTime.timestamp()` | `Float` | |
| `DateTime.astimezone(tz=none)` | `DateTime` | |
| `DateTime.weekday()` / `.isoweekday()` | `Int` | |
| `DateTime.isoformat(sep=none)` / `.strftime(fmt)` | `Str` | |
| `DateTime.replace(...)` | `DateTime` | |
| `DateTime + TimeDelta` | `DateTime` | |
| `DateTime - TimeDelta` | `DateTime` | |
| `DateTime - DateTime` | `TimeDelta` | |
| `DateTime < / <= / > / >= DateTime` | `Boolean` | |
| `TimeDelta(days=none, seconds=none, microseconds=none, milliseconds=none, minutes=none, hours=none, weeks=none)` | `TimeDelta` | |
| `TimeDelta.days` / `.seconds` / `.microseconds` (properties) | `Int` | |
| `TimeDelta.total_seconds()` | `Float` | |
| `TimeDelta + / - TimeDelta` | `TimeDelta` | |
| `TimeDelta * Int` | `TimeDelta` | |
| `TimeDelta / Int` | `TimeDelta` | |
| `TimeDelta / TimeDelta` | `Float` | ratio |
| `TimeDelta // TimeDelta` | `Int` | floor division |
| `TimeDelta // Int` | `TimeDelta` | |
| `TimeDelta % TimeDelta` | `TimeDelta` | |
| `-TimeDelta` | `TimeDelta` | |
| `TimeZone(offset, name=none)` | `TimeZone` | |
| `Date.min` / `Date.max` (class attrs) | `Date` | years 1 and 9999, mirroring the stdlib |
| `TimeZone.utc` (class attr) | `TimeZone` | UTC constant |
| `TimeZone.utcoffset(dt=none)` | `TimeDelta` | |
| `TimeZone.tzname(dt=none)` | `Str` | |

The `tzinfo` extension protocol (custom subclasses of Python's abstract `datetime.tzinfo`) is out of scope; users get `TimeZone` for fixed offsets. `Date.min`/`Date.max` are exposed as class attributes (`Date` instances for years 1 and 9999); the bare `datetime.MINYEAR`/`MAXYEAR` integer constants stay out — see the [permanent divergence](#no-datetimemaxyear--datetimeminyear) (the values are implicit in `Date.min`/`Date.max` and in the constructor's range check).

`datetime`, `Date`, `Time`, `DateTime`, `TimeDelta`, and `TimeZone` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/datetime.py` — namespace-only, no AST rewrite.

### re + Pattern + Match — `poop/types/re.py` + `poop/transformers/re.py`

`re` mirrors Python's `re` module — regular expression matching, substitution, splitting, and compilation. `Pattern` and `Match` are the two wrapper classes, exposed both as namespace attributes (`re.Pattern`, `re.Match`) and as bare globals (mirroring how `UUID` is also reachable without the `uuid.` prefix).

| Operation | Returns | Notes |
|---|---|---|
| `re.match(pattern, string, flags=none)` | `Match \| NoneClass` | anchored at start |
| `re.search(pattern, string, flags=none)` | `Match \| NoneClass` | anywhere |
| `re.fullmatch(pattern, string, flags=none)` | `Match \| NoneClass` | full string |
| `re.findall(pattern, string, flags=none)` | `List[Str]` or `List[Tuple]` | tuples when groups exist |
| `re.finditer(pattern, string, flags=none)` | `Tuple[Match]` | materialised eagerly — POOP collections are not lazy |
| `re.sub(pattern, repl, string, count=none, flags=none)` | `Str` | |
| `re.subn(pattern, repl, string, count=none, flags=none)` | `Tuple(Str, Int)` | new string + count |
| `re.split(pattern, string, maxsplit=none, flags=none)` | `List[Str]` | |
| `re.escape(pattern)` | `Str` | escape regex meta-chars |
| `re.compile(pattern, flags=none)` | `Pattern` | |
| `re.IGNORECASE` / `MULTILINE` / `DOTALL` / `VERBOSE` / `ASCII` / `UNICODE` / `LOCALE` / `DEBUG` / `NOFLAG` | `Int` | flag constants |
| `re.purge()` | `none` | clears the compiled-pattern cache |
| `Pattern.match` / `.search` / `.fullmatch` / `.findall` / `.finditer` / `.sub` / `.subn` / `.split` | same as module-level | reuses the compiled regex |
| `Pattern.pattern` / `.flags` / `.groups` / `.groupindex` (properties) | `Str` / `Int` / `Int` / `Dict[Str, Int]` | |
| `Match.group()` | `Str` | whole match |
| `Match.group(i_or_name)` | `Str \| NoneClass` | unmatched optional → `none` |
| `Match.group(a, b, ...)` | `Tuple` | multiple groups |
| `Match.groups(default=none)` | `Tuple` | all numbered groups |
| `Match.groupdict(default=none)` | `Dict[Str, Str \| NoneClass]` | named groups |
| `Match.start(group=none)` / `.end(group=none)` | `Int` | |
| `Match.span(group=none)` | `Tuple(Int, Int)` | |
| `Match.expand(template)` | `Str` | apply `\1` / `\g<name>` backrefs |
| `Match.string` / `.re` (properties) | `Str` / `Pattern` | |

`re` and the `Pattern` / `Match` classes are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/re.py` — namespace-only, no AST rewrite.

### hashlib + Hash — `poop/types/hash.py` + `poop/transformers/hashlib.py`

`hashlib` mirrors Python's `hashlib` module — message digests (MD5, SHA-1/2/3, BLAKE2, SHAKE) and key-derivation functions (PBKDF2, scrypt). The shortcut messages live directly on `Bytes` so common code reads `b"abc".sha256().hexdigest()` — the receiver carries the data, the message names the algorithm.

| Operation | Returns | Notes |
|---|---|---|
| `hashlib.new(name, data=none)` | `Hash` | generic constructor |
| `hashlib.file_digest(path, digest, /)` | `Hash` | `path` is a `Path` — receiver-type divergence from CPython's `fileobj` |
| `hashlib.algorithms_available` (class attr) | `FrozenSet[Str]` | every algorithm OpenSSL exposes locally |
| `hashlib.algorithms_guaranteed` (class attr) | `FrozenSet[Str]` | algorithms guaranteed on every platform |
| `hashlib.Hash` (class attr) | `type[Hash]` | the wrapper class itself |
| `b.md5()` / `.sha1()` / `.sha224()` / `.sha256()` / `.sha384()` / `.sha512()` | `Hash` | shortcut on `Bytes` |
| `b.blake2b()` / `.blake2s()` | `Hash` | BLAKE2 family |
| `b.sha3_224()` / `.sha3_256()` / `.sha3_384()` / `.sha3_512()` | `Hash` | SHA-3 family |
| `b.shake_128()` / `.shake_256()` | `Hash` | length is passed to `.digest(length)` / `.hexdigest(length)` |
| `b.pbkdf2_hmac(hash_name, salt, iterations, dklen=none)` | `Bytes` | receiver = password |
| `b.scrypt(*, salt, n, r, p, maxmem=none, dklen=none)` | `Bytes` | receiver = password; defaults `maxmem=0`, `dklen=64` |
| `Hash.update(data)` | `none` | mutates in place |
| `Hash.digest(length=none)` | `Bytes` | `length` is required for shake hashes, ignored by the rest |
| `Hash.hexdigest(length=none)` | `Str` | same shape as `.digest` |
| `Hash.copy()` | `Hash` | independent clone |
| `Hash.digest_size` / `.block_size` (property) | `Int` | |
| `Hash.name` (property) | `Str` | |

`Str` does not carry the shortcut messages — encoding must be explicit (`"abc".encode("utf-8").sha256()`). This mirrors Python's bytes/str split and keeps the encoding step visible.

`hashlib` and `Hash` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/hashlib.py` — namespace-only, no AST rewrite.

### string + Template — `poop/types/string.py` + `poop/transformers/string.py`

`string` mirrors Python's `string` module — ASCII character-class constants plus the `Template` class for `$variable` substitution. The constants live on the namespace; `Template` is exposed alongside it (PascalCase), matching the `hmac`/`HMAC` and `uuid`/`UUID` convention.

| Operation | Returns | Notes |
|---|---|---|
| `string.ascii_letters` / `ascii_lowercase` / `ascii_uppercase` (class attrs) | `Str` | |
| `string.digits` / `hexdigits` / `octdigits` (class attrs) | `Str` | |
| `string.punctuation` / `printable` / `whitespace` (class attrs) | `Str` | |
| `string.capwords(s, sep=none)` | `Str` | title-cases each word separated by `sep` (whitespace by default) |
| `Template(template_str)` | `Template` | source kept on `.template` |
| `Template.substitute(mapping)` | `Str` | raises `KeyError` on missing key |
| `Template.safe_substitute(mapping)` | `Str` | leaves missing `$name` in place |
| `Template.template` (property) | `Str` | original source string |

`string.Formatter` is deliberately out of scope — `Str.format` covers the common case.

`string` and `Template` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/string.py` — namespace-only, no AST rewrite.

### difflib + SequenceMatcher — `poop/types/difflib.py` + `poop/transformers/difflib.py`

`difflib` mirrors Python's `difflib` module — text-line diffs (`unified_diff`, `context_diff`, `ndiff`, `restore`), fuzzy matching (`get_close_matches`), and the element-wise `SequenceMatcher` class for detailed diff queries.

| Operation | Returns | Notes |
|---|---|---|
| `difflib.unified_diff(a, b, fromfile=none, tofile=none, fromfiledate=none, tofiledate=none, n=none, lineterm=none)` | `List[Str]` | `a` / `b` are `List[Str]` of lines |
| `difflib.context_diff(a, b, …)` | `List[Str]` | same arg shape as `unified_diff` |
| `difflib.ndiff(a, b, linejunk=none, charjunk=none)` | `List[Str]` | `?`/`-`/`+`/` ` marker per line; `linejunk` / `charjunk` are `Block`s routed through `block.bridge` (`charjunk=none` uses CPython's default `IS_CHARACTER_JUNK`) |
| `difflib.restore(seq, which)` | `List[Str]` | `which` is `Int(1)` or `Int(2)` |
| `difflib.get_close_matches(word, possibilities, n=none, cutoff=none)` | `List[Str]` | defaults match CPython (`n=3`, `cutoff=0.6`) |
| `SequenceMatcher(a, b, isjunk=none, autojunk=none)` | `SequenceMatcher` | `a` / `b` are `Str` (per-char) or `List[Str]` (per-line); `isjunk` is a `Block` routed through `block.bridge` |
| `SequenceMatcher.ratio()` / `.quick_ratio()` / `.real_quick_ratio()` | `Float` | |
| `SequenceMatcher.get_matching_blocks()` | `List[Tuple(Int, Int, Int)]` | `(a, b, size)` per block |
| `SequenceMatcher.get_opcodes()` | `List[Tuple(Str, Int, Int, Int, Int)]` | `(tag, i1, i2, j1, j2)` |
| `SequenceMatcher.find_longest_match(alo=none, ahi=none, blo=none, bhi=none)` | `Tuple(Int, Int, Int)` | |
| `Differ(linejunk=none, charjunk=none)` | `Differ` | constructor accepts `Block` predicates |
| `Differ.compare(a, b)` | `List[Str]` | marker-prefixed line diff |
| `HtmlDiff(tabsize=none, wrapcolumn=none, linejunk=none, charjunk=none)` | `HtmlDiff` | HTML diff renderer |
| `HtmlDiff.make_file(fromlines, tolines, fromdesc=none, todesc=none, context=false, numlines=none)` / `.make_table(...)` | `Str` | full HTML document / inner `<table>` only |
| `difflib.IS_CHARACTER_JUNK(ch, ws=none)` / `.IS_LINE_JUNK(line)` | `Boolean` | default predicates exposed for reuse |

`difflib`, `SequenceMatcher`, `Differ`, and `HtmlDiff` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/difflib.py` — namespace-only, no AST rewrite.

### textwrap + TextWrapper — `poop/types/textwrap.py` + `poop/transformers/textwrap.py`

`textwrap` mirrors Python's `textwrap` module — reflowing multi-line strings. Module-level shortcuts cover the common cases; the reusable `TextWrapper` class captures the full set of wrapping knobs.

| Operation | Returns | Notes |
|---|---|---|
| `textwrap.wrap(text, width=none, …)` | `List[Str]` | defaults: `width=70`, etc. |
| `textwrap.fill(text, width=none, …)` | `Str` | same arg shape as `wrap` |
| `textwrap.shorten(text, width, placeholder=none)` | `Str` | truncates with `" [...]"` by default |
| `textwrap.indent(text, prefix, predicate=none)` | `Str` | `predicate` is a `Block` / Python callable that takes `Str`, returns truthy |
| `textwrap.dedent(text)` | `Str` | removes common leading indent |
| `TextWrapper(width=none, initial_indent=none, subsequent_indent=none, expand_tabs=none, replace_whitespace=none, drop_whitespace=none, fix_sentence_endings=none, break_long_words=none, break_on_hyphens=none, tabsize=none, max_lines=none, placeholder=none)` | `TextWrapper` | reusable instance |
| `TextWrapper.wrap(text)` / `.fill(text)` | `List[Str]` / `Str` | reuses configured knobs |

`textwrap` and `TextWrapper` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/textwrap.py` — namespace-only, no AST rewrite.

### unicodedata — `poop/types/unicodedata.py` + `poop/transformers/unicodedata.py`

`unicodedata` mirrors Python's `unicodedata` module — access to the Unicode Character Database: normalization, character properties, name lookup, and numeric values. No new POOP type; every method takes/returns plain `Str` / `Int` / `Float` / `Boolean`.

| Operation | Returns | Notes |
|---|---|---|
| `unicodedata.normalize(form, unistr)` | `Str` | `form` is `"NFC"` / `"NFKC"` / `"NFD"` / `"NFKD"` |
| `unicodedata.is_normalized(form, unistr)` | `Boolean` | |
| `unicodedata.category(chr)` | `Str` | e.g. `"Lu"`, `"Nd"`, `"Po"` |
| `unicodedata.bidirectional(chr)` | `Str` | empty for unassigned |
| `unicodedata.combining(chr)` | `Int` | canonical combining class |
| `unicodedata.east_asian_width(chr)` | `Str` | `"Na"`, `"W"`, `"F"`, `"H"`, `"A"`, `"N"` |
| `unicodedata.mirrored(chr)` | `Int` | `0` or `1` |
| `unicodedata.decomposition(chr)` | `Str` | empty when no decomposition exists |
| `unicodedata.name(chr, default=none)` | `Str` | raises `ValueError` when no name and no default |
| `unicodedata.lookup(name)` | `Str` | raises `KeyError` on unknown name |
| `unicodedata.decimal(chr, default=none)` | `Int` | raises `ValueError` when not a decimal digit and no default |
| `unicodedata.digit(chr, default=none)` | `Int` | same shape as `decimal` |
| `unicodedata.numeric(chr, default=none)` | `Float` | covers fractions like `"½"` (0.5) |
| `unicodedata.unidata_version` (class attr) | `Str` | the Unicode version Python was built against |

The private `ucd_3_2_0` legacy UCD object is out of scope for v1.

`unicodedata` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/unicodedata.py` — namespace-only, no AST rewrite.

### zoneinfo + ZoneInfo — `poop/types/zoneinfo.py` + `poop/transformers/zoneinfo.py`

`zoneinfo` mirrors Python's `zoneinfo` module — IANA timezone database access. `ZoneInfo` is a `datetime.tzinfo` wrapper that pairs directly with the `datetime` namespace's `DateTime.now(tz=…)` / `.astimezone(tz)` / `DateTime(..., tzinfo=…)` entry points (all widened to accept either `TimeZone` or `ZoneInfo`).

| Operation | Returns | Notes |
|---|---|---|
| `ZoneInfo(key)` | `ZoneInfo` | cached lookup by IANA name |
| `ZoneInfo.no_cache(key)` (classmethod) | `ZoneInfo` | bypass the cache |
| `ZoneInfo.clear_cache(only_keys=none)` (classmethod) | `none` | `only_keys` is an optional `Set[Str]` |
| `ZoneInfo.key` (property) | `Str` | the IANA name |
| `zoneinfo.available_timezones()` | `Set[Str]` | roster from the local tzdata |
| `zoneinfo.reset_tzpath(to=none)` | `none` | `to` is an optional `Tuple[Str]` of search paths |
| `zoneinfo.TZPATH` | `Tuple[Str]` | current search path (property; `reset_tzpath` mutates it) |
| `zoneinfo.ZoneInfoNotFoundError` (class attr) | exception class | use with `Try.except_(...)` |

`ZoneInfo.from_file` is deferred — POOP has no file-object abstraction. `InvalidTZPathWarning` is out of scope (POOP has no warning system).

`zoneinfo` and `ZoneInfo` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/zoneinfo.py` — namespace-only, no AST rewrite.

### calendar + Calendar — `poop/types/calendar.py` + `poop/transformers/calendar.py`

`calendar` mirrors Python's `calendar` module — formatting month/year calendars, leap-year queries, weekday math. The reusable `Calendar` class iterates dates with a configurable first-weekday.

| Operation | Returns | Notes |
|---|---|---|
| `calendar.isleap(year)` | `Boolean` | |
| `calendar.leapdays(y1, y2)` | `Int` | |
| `calendar.weekday(year, month, day)` | `Int` | `0`=Monday |
| `calendar.monthrange(year, month)` | `Tuple(Int, Int)` | `(first_weekday, ndays)` |
| `calendar.monthcalendar(year, month)` | `List[List[Int]]` | rows of week × day; `0` for days outside the month |
| `calendar.month(year, month, w=none, l=none)` | `Str` | text rendering |
| `calendar.calendar(year, w=none, l=none, c=none, m=none)` | `Str` | full-year text rendering |
| `calendar.timegm(time_tuple)` | `Int` | inverse of `time.gmtime` |
| `calendar.MONDAY` … `SUNDAY` (class attrs) | `Int` | weekday constants (`0` … `6`) |
| `calendar.JANUARY` … `DECEMBER` (class attrs) | `Int` | month constants (`1` … `12`) |
| `calendar.IllegalMonthError` / `IllegalWeekdayError` (class attrs) | exception class | use with `Try.except_(...)` |
| `Calendar(firstweekday=none)` | `Calendar` | reusable iterator |
| `Calendar.iterweekdays()` | `List[Int]` | weekday order |
| `Calendar.itermonthdates(year, month)` | `List[Date]` | full weeks including padding days |
| `Calendar.itermonthdays(year, month)` | `List[Int]` | `0` for padding |
| `Calendar.itermonthdays2(year, month)` | `List[Tuple(Int, Int)]` | `(day, weekday)` |
| `Calendar.itermonthdays3(year, month)` | `List[Tuple(Int, Int, Int)]` | `(year, month, day)` — no padding |
| `Calendar.monthdatescalendar(year, month)` | `List[List[Date]]` | weeks of full `Date`s |
| `Calendar.monthdayscalendar(year, month)` | `List[List[Int]]` | weeks of day numbers |
| `Calendar.yeardatescalendar(year, width=none)` | nested `List` | row × month × week × day |

POOP collections are materialized eagerly — the `iter*` methods return `List` instead of Python's generators. `HTMLCalendar`, `LocaleTextCalendar`, and `LocaleHTMLCalendar` are out of scope for v1.

`calendar` and `Calendar` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/calendar.py` — namespace-only, no AST rewrite.

### array + Array — `poop/types/array.py` + `poop/transformers/array.py`

`array` mirrors Python's `array` module — a homogeneous, memory-compact sequence keyed by a single typecode. Integer typecodes (`b`/`B`/`h`/`H`/`i`/`I`/`l`/`L`/`q`/`Q`) take `Int`; float typecodes (`f`/`d`) take `Float`. Typecode `u` (deprecated upstream) is intentionally omitted — use `List[Str]` for character data.

| Operation | Returns | Notes |
|---|---|---|
| `Array(typecode, initializer=none)` | `Array` | initializer is `List` or `Bytes` |
| `Array.typecode` (property) | `Str` | |
| `Array.itemsize` (property) | `Int` | bytes per element |
| `Array.len()` | `Int` | |
| `Array.at(i)` / `.slice(start, stop, step=none)` | element / `Array` | |
| `Array.append(v)` / `.extend(other)` / `.insert(i, v)` | `none` | mutators |
| `Array.pop(i=none)` / `.remove(v)` | element / `none` | |
| `Array.count(v)` / `.index(v)` | `Int` | |
| `Array.reverse()` | `none` | in-place |
| `Array.tobytes()` / `.tolist()` | `Bytes` / `List` | conversion |
| `Array.frombytes(b)` / `.fromlist(l)` | `none` | extend from raw |
| `Array.do(block)` | `none` | per-element iteration |
| `Array.includes(v)` | `Boolean` | |
| `array.typecodes` (class attr) | `Str` | valid typecode characters |

`array.fromfile`/`tofile` are deferred — POOP has no file-streaming abstraction.

`array` and `Array` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/array.py` — namespace-only, no AST rewrite.

### weakref + WeakRef + WeakSet + WeakKeyDictionary + WeakValueDictionary — `poop/types/weakref.py` + `poop/transformers/weakref.py`

`weakref` mirrors Python's `weakref` module — references that don't prevent garbage collection. Useful for caches and breaking cycles. POOP user-class instances support weak references (they have `__weakref__` automatically); POOP built-in primitives like `Int`/`Str`/`Bytes` define `__slots__` without `__weakref__`, matching Python's `int`/`str` restriction.

| Operation | Returns | Notes |
|---|---|---|
| `weakref.ref(obj, callback=none)` | `WeakRef` | |
| `weakref.proxy(obj, callback=none)` | transparent proxy | forwards attribute access while live |
| `weakref.getweakrefcount(obj)` | `Int` | |
| `weakref.getweakrefs(obj)` | `List[WeakRef]` | |
| `WeakRef(obj, callback=none)` | `WeakRef` | calling the ref (`r()`) or `.get()` returns the live object or `none` |
| `WeakRef.is_alive()` | `Boolean` | |
| `WeakSet(items=none)` | `WeakSet` | `.add` / `.discard` / `.remove` / `.includes` / `.len()` / iteration / `.clear()` / `.copy()` |
| `WeakKeyDictionary()` | `WeakKeyDictionary` | `.at_put(k, v)` / `.at(k)` / `.get(k, default=none)` / `.includes(k)` / `.keys()` / `.values()` / `.clear()` |
| `WeakValueDictionary()` | `WeakValueDictionary` | same surface as `WeakKeyDictionary` |

`finalize` and `WeakMethod` are out of scope for v1.

`weakref`, `WeakRef`, `WeakSet`, `WeakKeyDictionary`, and `WeakValueDictionary` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/weakref.py` — namespace-only, no AST rewrite.

### enum + Enum + IntEnum + StrEnum + Flag + IntFlag + ReprEnum — `poop/types/enum.py` + `poop/transformers/enum.py`

`enum` mirrors Python's `enum` module — typed enumeration classes (`class Color(Enum): RED = 1`). The standard CPython machinery is preserved (members, lookups, `@unique`, `auto()`, etc.) and POOP adds:

- `.name_str()` returning POOP `Str` — `.name` itself stays a Python `str` because CPython's enum machinery (and decorators like `@unique`) compare it for identity.
- `.value_object()` returning a wrapped POOP value (`Int`/`Str`/`Float`/`Boolean`) — `.value` returns whatever was assigned (raw Python primitives stay raw; POOP types pass through unchanged).
- `_missing_` is wired so `Color(Int(1))` resolves to `Color.RED` exactly like `Color(1)`.
- `Enum.iter()` returns a POOP `List` of members.

| Operation | Returns | Notes |
|---|---|---|
| `class Color(Enum): RED = 1` | enum class | members are class-side singletons |
| `Color.RED.name` | Python `str` | matches Python's enum protocol |
| `Color.RED.name_str()` | `Str` | POOP-shaped name |
| `Color.RED.value` | whatever was assigned | raw Python primitive or POOP type |
| `Color.RED.value_object()` | `Int` / `Str` / `Float` / `Boolean` | wrapped POOP form |
| `Color(value)` / `Color(Int(value))` | enum member | POOP wrappers are unwrapped before lookup |
| `Color.iter()` | `List` | materialized member list |
| `IntEnum` / `StrEnum` / `Flag` / `IntFlag` | enum classes | same POOP helpers, plus the data-type mixin from CPython |
| `ReprEnum` | enum class (re-exported) | requires a data-type mixin (`class Color(int, ReprEnum): ...`); `.name`/`.value` stay raw Python types in this path |
| `auto()` | sentinel | for sequential value generation inside an enum body |
| `enum.unique` / `verify` / `member` / `nonmember` (class attrs) | decorators | apply directly on enum classes |
| `enum.CONTINUOUS` / `NAMED_FLAGS` / `UNIQUE` (class attrs) | constants | for `@verify` |

`EnumType` metaclass access is out of scope (POOP forbids introspection).

`enum`, `Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `ReprEnum`, and `auto` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/enum.py` — namespace-only, no AST rewrite.

### fractions + Fraction — `poop/types/fractions.py` + `poop/transformers/fractions.py`

`fractions` mirrors Python's `fractions` module — exact rational arithmetic. `Fraction` is bare alongside the lowercase namespace (matching the `uuid` / `UUID` convention).

| Operation | Returns | Notes |
|---|---|---|
| `Fraction(numerator=none, denominator=none)` | `Fraction` | two-arg form takes `Int`s; one-arg form accepts `Int` / `Float` / `Str("3/4")` / `Str("0.25")` / `Fraction` |
| `Fraction.from_float(f)` (classmethod) | `Fraction` | exact bit-pattern from `Float` |
| `Fraction.from_decimal(d)` (classmethod) | `Fraction` | exact from `Decimal` |
| `Fraction.numerator` / `.denominator` (properties) | `Int` | always reduced to lowest terms |
| `Fraction.limit_denominator(max_denominator=none)` | `Fraction` | best rational with denominator ≤ max |
| `Fraction.as_integer_ratio()` | `Tuple(Int, Int)` | `(numerator, denominator)` |
| `Fraction + - * / // % **` | `Fraction` / `Int` / `Float` | mixing with `Int` keeps `Fraction`; `Float` promotes to `Float`; `Fraction // Fraction` → `Int` |
| `Fraction == != < <= > >= abs +x -x` | as Python | standard comparisons |

POOP `Int` / `Float` don't return `NotImplemented` for non-POOP operands, so reflected dunders (`__radd__`, `__rsub__`, `__rmul__`, `__rtruediv__`) are only reachable when invoked directly — `Int + Fraction` won't dispatch through them yet.

`fractions` and `Fraction` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/fractions.py` — namespace-only, no AST rewrite.

### statistics + NormalDist — `poop/types/statistics.py` + `poop/transformers/statistics.py`

`statistics` mirrors Python's `statistics` module — central tendency, spread, quantiles, correlation primitives, and the `NormalDist` distribution class.

| Operation | Returns | Notes |
|---|---|---|
| `statistics.mean(data)` | element | typically `Float` / `Int` / `Fraction` depending on input |
| `statistics.fmean(data, weights=none)` | `Float` | always `Float` |
| `statistics.geometric_mean(data)` | `Float` | |
| `statistics.harmonic_mean(data, weights=none)` | `Float` | |
| `statistics.median(data)` | `Float` / `Int` | even-count averages two middle elements |
| `statistics.median_low(data)` / `.median_high(data)` | element | |
| `statistics.median_grouped(data, interval=none)` | `Float` | |
| `statistics.mode(data)` / `.multimode(data)` | element / `List` | works on `Str` / `Boolean` / numeric data |
| `statistics.pstdev(data, mu=none)` / `.pvariance(data, mu=none)` | `Float` | population spread |
| `statistics.stdev(data, xbar=none)` / `.variance(data, xbar=none)` | `Float` | sample spread |
| `statistics.quantiles(data, n=none, method=none)` | `List[Float]` | default `n=4`, `method="exclusive"` |
| `statistics.correlation(x, y, method=none)` | `Float` | `method` is `"linear"` (default) or `"ranked"` |
| `statistics.covariance(x, y)` | `Float` | |
| `statistics.linear_regression(x, y, proportional=none)` | `Tuple(Float, Float)` | `(slope, intercept)` |
| `statistics.StatisticsError` (class attr) | exception class | for `Try.except_` on empty/invalid data |
| `NormalDist(mu=none, sigma=none)` | `NormalDist` | |
| `NormalDist.from_samples(data)` (classmethod) | `NormalDist` | |
| `NormalDist.mean` / `.stdev` / `.variance` / `.median` / `.mode` (properties) | `Float` | |
| `NormalDist.cdf(x)` / `.pdf(x)` / `.inv_cdf(p)` / `.zscore(x)` | `Float` | |
| `NormalDist.samples(n, seed=none)` | `List[Float]` | |
| `NormalDist.overlap(other)` | `Float` | |
| `NormalDist.quantiles(n=none)` | `List[Float]` | default `n=4` |
| `NormalDist + - NormalDist` / `NormalDist + - * / Float` | `NormalDist` | affine transformations; `+` / `-` between two `NormalDist`s sums means and combines variances |
| `NormalDist == != hash` | as Python | |

The `_sum` private helper is out of scope. Decimal-aware variants surface naturally through the existing `Decimal` integration.

`statistics` and `NormalDist` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/statistics.py` — namespace-only, no AST rewrite.

### struct + Struct — `poop/types/struct.py` + `poop/transformers/struct.py`

`struct` mirrors Python's `struct` module — packing and unpacking binary data via format strings (`>I`, `<2sH`, `?fd`, …). Format-char wrapping back into POOP types is handled at the boundary: `int` → `Int`, `float` → `Float`, `bool` → `Boolean`, `bytes` → `Bytes`. Buffers accept `Bytes` / `ByteArray` / `MemoryView` for reads; writes require a mutable buffer (`ByteArray` or `MemoryView`).

| Operation | Returns | Notes |
|---|---|---|
| `struct.pack(format, *values)` | `Bytes` | each value is `Int` / `Float` / `Boolean` / `Bytes` / `Str` |
| `struct.unpack(format, buffer)` | `Tuple` | elements wrapped to POOP types per format char |
| `struct.pack_into(format, buffer, offset, *values)` | `none` | `buffer` must be `ByteArray` / `MemoryView` |
| `struct.unpack_from(format, buffer, offset=none)` | `Tuple` | default offset is `0` |
| `struct.iter_unpack(format, buffer)` | `List[Tuple]` | materialized — POOP collections are not lazy |
| `struct.calcsize(format)` | `Int` | |
| `struct.error` (class attr) | exception class | for `Try.except_` on format mismatches |
| `Struct(format)` | `Struct` | pre-compiled format for reuse |
| `Struct.format` / `.size` (properties) | `Str` / `Int` | |
| `Struct.pack` / `.unpack` / `.pack_into` / `.unpack_from` / `.iter_unpack` | same as module-level | reuses the compiled format |

`struct` and `Struct` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/struct.py` — namespace-only, no AST rewrite.

### codecs + CodecInfo — `poop/types/codecs.py` + `poop/transformers/codecs.py`

`codecs` mirrors Python's `codecs` module — the codec registry behind `Str.encode` / `Bytes.decode`. The common encode/decode shortcuts on `Str` and `Bytes` already cover most needs; this namespace surfaces the codecs that don't fit the standard text/bytes split (`rot_13`, `hex_codec`, `base64_codec`, …) plus the BOM constants and registry lookups.

| Operation | Returns | Notes |
|---|---|---|
| `codecs.encode(obj, encoding=none, errors=none)` | `Bytes` / `Str` | text codecs return `Str`; binary codecs return `Bytes` |
| `codecs.decode(obj, encoding=none, errors=none)` | `Bytes` / `Str` | same polymorphic shape as `encode` |
| `codecs.lookup(encoding)` | `CodecInfo` | raises `LookupError` on unknown names |
| `codecs.BOM_UTF8` / `BOM_UTF16` / `BOM_UTF16_LE` / `BOM_UTF16_BE` / `BOM_UTF32` / `BOM_UTF32_LE` / `BOM_UTF32_BE` / `BOM` / `BOM_LE` / `BOM_BE` (class attrs) | `Bytes` | standard byte-order marks |
| `codecs.CodecInfo` (class attr) | `type[CodecInfo]` | wrapper class |
| `CodecInfo.name` (property) | `Str` | canonical codec name |
| `CodecInfo.encode(obj, errors=none)` / `.decode(obj, errors=none)` | `Tuple(result, length)` | `(Bytes`/`Str, Int)` |
| `CodecInfo.incrementalencoder` / `.incrementaldecoder` (properties) | Python class | raw refs for callers that need streaming |

Incremental encoder/decoder construction, `StreamReader` / `StreamWriter`, and the `register` / `register_error` extension hooks are out of scope for v1 — they pair with future streaming I/O.

`codecs` and `CodecInfo` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/codecs.py` — namespace-only, no AST rewrite.

### filecmp + Dircmp — `poop/types/filecmp.py` + `poop/transformers/filecmp.py`

`filecmp` mirrors Python's `filecmp` module — shallow/metadata or full-content file and directory comparison. `Dircmp` is exposed bare alongside the lowercase namespace.

| Operation | Returns | Notes |
|---|---|---|
| `filecmp.cmp(f1, f2, shallow=none)` | `Boolean` | default `shallow=true` |
| `filecmp.cmpfiles(dir1, dir2, common, shallow=none)` | `Tuple(List[Str], List[Str], List[Str])` | `(match, mismatch, errors)` |
| `filecmp.clear_cache()` | `none` | drops the metadata-based fast-path cache |
| `filecmp.DEFAULT_IGNORES` (class attr) | `List[Str]` | snapshot of CPython's default-skip list |
| `Dircmp(a, b, ignore=none, hide=none)` | `Dircmp` | recursive comparison root |
| `Dircmp.left` / `.right` (properties) | `Str` | the original paths |
| `Dircmp.left_only` / `.right_only` / `.common` / `.common_dirs` / `.common_files` / `.common_funny` / `.same_files` / `.diff_files` / `.funny_files` (properties) | `List[Str]` | name groupings |
| `Dircmp.subdirs` (property) | `Dict[Str, Dircmp]` | per-subdir comparison nodes |
| `Dircmp.report()` / `.report_partial_closure()` / `.report_full_closure()` | `none` | writes the summary to stdout |
| `Dircmp.report_str()` | `Str` | captures `report()` output instead of printing |

`filecmp` and `Dircmp` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/filecmp.py` — namespace-only, no AST rewrite.

### tempfile + TemporaryFile / NamedTemporaryFile / SpooledTemporaryFile / TemporaryDirectory — `poop/types/tempfile.py` + `poop/transformers/tempfile.py`

`tempfile` mirrors Python's `tempfile` module — secure temp files and directories. Module-level factories return `Path` (or `Tuple(Int, Path)` for `mkstemp` exposing the raw file descriptor); the four temp classes are `With`-friendly and expose minimal binary `.read` / `.write` / `.seek` / `.tell` / `.flush` / `.close` so callers can populate or drain a file without a separate POOP I/O abstraction.

| Operation | Returns | Notes |
|---|---|---|
| `tempfile.mkstemp(suffix=none, prefix=none, dir=none, text=none)` | `Tuple(Int, Path)` | `(fd, path)` — close `fd` with `os.close` after use |
| `tempfile.mkdtemp(suffix=none, prefix=none, dir=none)` | `Path` | |
| `tempfile.gettempdir()` | `Path` | |
| `tempfile.gettempprefix()` | `Str` | |
| `tempfile.gettempdirb()` | `Bytes` | |
| `tempfile.gettempprefixb()` | `Bytes` | |
| `tempfile.tempdir` | `Path` / `none` | current search-path override (read property) |
| `tempfile.tempdir = path` | `none` | setter — assign a `Path`/`Str` or `none` to clear |
| `TemporaryDirectory(suffix=none, prefix=none, dir=none, ignore_cleanup_errors=none)` | `TemporaryDirectory` | `.name` returns `Path`; `.cleanup()` removes; `With` yields the `Path` |
| `TemporaryFile(mode=none, suffix=none, prefix=none, dir=none)` | `TemporaryFile` | anonymous file; `With` yields the wrapper |
| `NamedTemporaryFile(mode=none, …, delete=none)` | `NamedTemporaryFile` | `.name` returns `Path`; default `delete=true` |
| `SpooledTemporaryFile(max_size=none, mode=none, …)` | `SpooledTemporaryFile` | `.rollover()` forces flush to disk |
| `_TempFileBase.write(data)` / `.read(size=none)` / `.seek(offset, whence=none)` / `.tell()` / `.flush()` / `.close()` | varies | binary by default; pass `mode=Str("w+")` for text |

The private `_RandomNameSequence` class is out of scope for v1.

`tempfile`, `TemporaryFile`, `NamedTemporaryFile`, `SpooledTemporaryFile`, and `TemporaryDirectory` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/tempfile.py` — namespace-only, no AST rewrite.

### shutil — `poop/types/shutil.py` + `poop/transformers/shutil.py`

`shutil` mirrors Python's `shutil` module — high-level file operations: copy/move/remove trees, archive create/extract, disk and terminal info. Paths accept either `Path` or `Str` everywhere; return values are `Path` when CPython returns a path-like.

| Operation | Returns | Notes |
|---|---|---|
| `shutil.copy(src, dst, follow_symlinks=none)` / `.copy2(...)` / `.copyfile(...)` | `Path` | metadata-aware variants follow CPython |
| `shutil.copytree(src, dst, symlinks=none, ignore=none, copy_function=none, ignore_dangling_symlinks=none, dirs_exist_ok=none)` | `Path` | recursive; `ignore` / `copy_function` accept `Block`s |
| `shutil.ignore_patterns(*patterns)` | `Block` | factory for `copytree(ignore=...)` |
| `shutil.copymode(src, dst, follow_symlinks=none)` / `.copystat(...)` | `none` | metadata-only copies |
| `shutil.move(src, dst, copy_function=none)` | `Path` | `copy_function` accepts a `Block` |
| `shutil.rmtree(path, ignore_errors=none)` | `none` | recursive remove |
| `shutil.which(cmd, mode=none, path=none)` | `Path` / `none` | locate executable on `PATH` |
| `shutil.make_archive(base_name, format, root_dir=none, base_dir=none)` | `Path` | `format` is `"zip"`, `"tar"`, `"gztar"`, …  |
| `shutil.unpack_archive(filename, extract_dir=none, format=none)` | `none` | |
| `shutil.get_archive_formats()` | `List[Tuple(Str, Str)]` | `(name, description)` |
| `shutil.get_unpack_formats()` | `List[Tuple(Str, List[Str], Str)]` | `(name, extensions, description)` |
| `shutil.disk_usage(path)` | `Tuple(Int, Int, Int)` | `(total, used, free)` in bytes |
| `shutil.get_terminal_size(fallback=none)` | `Tuple(Int, Int)` | `(columns, lines)` |
| `shutil.chown(path, user=none, group=none)` | `none` | |
| `shutil.Error` / `.SameFileError` (class attrs) | exception class | for `Try.except_` |

`copytree(ignore=, copy_function=)` and `move(copy_function=)` accept POOP `Block`s routed through `block.bridge`. `shutil.ignore_patterns(*patterns)` returns a POOP `Block` that drops in directly to `copytree(ignore=...)`.

`shutil` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/shutil.py` — namespace-only, no AST rewrite.

### pickle + Pickler + Unpickler — `poop/types/pickle.py` + `poop/transformers/pickle.py`

`pickle` mirrors Python's `pickle` module — object serialization to `Bytes`. The namespace adopts the same round-trip discipline as `json`: POOP primitive wrappers (`Int` / `Str` / `Float` / `Bytes` / `Boolean` / `NoneClass`) and POOP collections (`List` / `Tuple` / `Dict` / `Set` / `FrozenSet`) are unwrapped to their Python equivalents on dump and re-wrapped on load, so callers never see a raw Python primitive on the way out. POOP user-class instances pass through unchanged. `dump` / `load` are path-based per POOP's file-I/O convention (no `open` in POOP).

| Operation | Returns | Notes |
|---|---|---|
| `pickle.dumps(obj, protocol=none)` | `Bytes` | `protocol` defaults to `pickle.DEFAULT_PROTOCOL` |
| `pickle.loads(data)` | wrapped POOP value | inverse of `dumps` |
| `pickle.dump(obj, path, protocol=none)` | `none` | path-based; no file-object parameter |
| `pickle.load(path)` | wrapped POOP value | |
| `pickle.HIGHEST_PROTOCOL` / `pickle.DEFAULT_PROTOCOL` (class attrs) | `Int` | |
| `pickle.PickleError` / `pickle.PicklingError` / `pickle.UnpicklingError` (class attrs) | exception classes | for `Try.except_` |
| `Pickler(protocol=none)` | `Pickler` | in-memory buffer Pickler |
| `Pickler.dump(obj)` | `none` | accumulates into the internal buffer |
| `Pickler.getvalue()` | `Bytes` | the accumulated stream |
| `Pickler.clear_memo()` | `none` | |
| `Pickler.fast` (inherited C attr) | `int` (0 / 1) | mirrors the deprecated upstream knob; raw Python because the C extension bypasses Python descriptors |
| Subclass `Pickler` and override `persistent_id(obj)` | — | override receives POOP value, returns POOP id or `none` (routed via `block.bridge`) |
| `pickler.dispatch_table = {Type: Block(reducer)}` | `Dict` or `dict` | per-entry `Block` reducers are bridged on assignment; reading returns the bridged dict (or raises `AttributeError` when unset, matching CPython's "no table" sentinel). Class-level `dispatch_table = ...` in subclasses is **not** auto-bridged — assign as instance attribute |
| `Unpickler(data)` | `Unpickler` | wraps a `Bytes` buffer |
| `Unpickler.load()` | wrapped POOP value | reads the next pickled object |
| Subclass `Unpickler` and override `persistent_load(pid)` | — | override receives POOP `pid`, returns POOP object (routed via `block.bridge`) |

POOP's `Int` / `Str` / `Float` / … wrappers set `__module__` / `__name__` for pretty printing, which would otherwise make them unpicklable by reference; the `_unwrap` / `_wrap` boundary sidesteps that entirely. `pickletools` (introspection of pickle streams) and the `__reduce__` protocol hook are out of scope for v1 — POOP user classes can implement `__reduce__`, but the protocol isn't formally documented here.

**Security note:** `pickle.loads` / `Unpickler.load` execute arbitrary code embedded in the byte stream. Never load pickles from untrusted sources.

`pickle`, `Pickler`, and `Unpickler` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/pickle.py` — namespace-only, no AST rewrite.

### zlib + Compress + Decompress — `poop/types/zlib.py` + `poop/transformers/zlib.py`

`zlib` mirrors Python's `zlib` module — DEFLATE compression plus CRC32 / Adler32 checksums. `Compress` and `Decompress` are POOP wrappers around `zlib.compressobj`/`decompressobj` for streaming.

| Operation | Returns | Notes |
|---|---|---|
| `zlib.compress(data, level=none, wbits=none)` | `Bytes` | default level = `Z_DEFAULT_COMPRESSION` |
| `zlib.decompress(data, wbits=none, bufsize=none)` | `Bytes` | |
| `zlib.compressobj(level=none, method=none, wbits=none, memLevel=none, strategy=none, zdict=none)` | `Compress` | |
| `zlib.decompressobj(wbits=none, zdict=none)` | `Decompress` | |
| `zlib.adler32(data, value=none)` / `.crc32(data, value=none)` | `Int` | rolling checksums |
| `zlib.MAX_WBITS` / `DEFLATED` / `DEF_MEM_LEVEL` / `DEF_BUF_SIZE` / `Z_*_*` (class attrs) | `Int` | upstream constants |
| `zlib.ZLIB_VERSION` (class attr) | Python `str` | banner |
| `zlib.error` (class attr) | exception class | for `Try.except_` |
| `Compress.compress(data)` / `.flush(mode=none)` / `.copy()` | `Bytes` / `Compress` | streaming |
| `Decompress.decompress(data, max_length=none)` / `.flush(length=none)` / `.copy()` | `Bytes` / `Decompress` | |
| `Decompress.unused_data` / `.unconsumed_tail` / `.eof` | `Bytes` / `Bytes` / `bool` | streaming cursor state |

`zlib`, `Compress`, and `Decompress` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/zlib.py` — namespace-only, no AST rewrite.

### gzip + GzipFile — `poop/types/gzip.py` + `poop/transformers/gzip.py`

`gzip` mirrors Python's `gzip` module — RFC 1952 gzip files built on top of `zlib`. `GzipFile` is a path-based, `With`-friendly file handle.

| Operation | Returns | Notes |
|---|---|---|
| `gzip.compress(data, compresslevel=none)` | `Bytes` | default `compresslevel=9` |
| `gzip.decompress(data)` | `Bytes` | |
| `gzip.open(path, mode=none, compresslevel=none)` | `GzipFile` | path-based; no file-object parameter |
| `gzip.BadGzipFile` (class attr) | exception class | for `Try.except_` |
| `GzipFile.read(size=none)` / `.write(data)` | `Bytes` / `Int` | |
| `GzipFile.seek(offset, whence=none)` / `.tell()` / `.flush()` / `.close()` | mixed | streaming cursor |

`gzip` and `GzipFile` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/gzip.py` — namespace-only, no AST rewrite.

### bz2 + BZ2File + BZ2Compressor + BZ2Decompressor — `poop/types/bz2.py` + `poop/transformers/bz2.py`

`bz2` mirrors Python's `bz2` module — bzip2 compression. Same shape as `gzip` plus a streaming compressor/decompressor pair.

| Operation | Returns | Notes |
|---|---|---|
| `bz2.compress(data, compresslevel=none)` | `Bytes` | default `compresslevel=9` |
| `bz2.decompress(data)` | `Bytes` | |
| `bz2.open(path, mode=none, compresslevel=none)` | `BZ2File` | |
| `BZ2File.read` / `.write` / `.seek` / `.tell` / `.flush` / `.close` | mixed | as in `GzipFile` |
| `BZ2Compressor(compresslevel=none)` / `.compress(data)` / `.flush()` | `BZ2Compressor` / `Bytes` | |
| `BZ2Decompressor()` / `.decompress(data, max_length=none)` | `BZ2Decompressor` / `Bytes` | |
| `BZ2Decompressor.eof` / `.needs_input` / `.unused_data` | `bool` / `bool` / `Bytes` | streaming state |

`bz2`, `BZ2File`, `BZ2Compressor`, and `BZ2Decompressor` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/bz2.py` — namespace-only, no AST rewrite.

### lzma + LZMAFile + LZMACompressor + LZMADecompressor — `poop/types/lzma.py` + `poop/transformers/lzma.py`

`lzma` mirrors Python's `lzma` module — LZMA / XZ compression. Same shape as `gzip`/`bz2`.

| Operation | Returns | Notes |
|---|---|---|
| `lzma.compress(data, format=none, check=none, preset=none)` | `Bytes` | |
| `lzma.decompress(data, format=none, memlimit=none)` | `Bytes` | |
| `lzma.open(path, mode=none, format=none, check=none, preset=none)` | `LZMAFile` | |
| `lzma.is_check_supported(check)` | `bool` | |
| `lzma.FORMAT_XZ` / `FORMAT_ALONE` / `FORMAT_RAW` / `FORMAT_AUTO` (class attrs) | `Int` | container formats |
| `lzma.CHECK_NONE` / `CHECK_CRC32` / `CHECK_CRC64` / `CHECK_SHA256` / `CHECK_ID_MAX` / `CHECK_UNKNOWN` (class attrs) | `Int` | integrity checks |
| `lzma.PRESET_DEFAULT` / `PRESET_EXTREME` (class attrs) | `Int` | preset shortcuts |
| `lzma.LZMAError` (class attr) | exception class | |
| `LZMACompressor(format=none, check=none, preset=none)` / `.compress(data)` / `.flush()` | `LZMACompressor` / `Bytes` | |
| `LZMADecompressor(format=none, memlimit=none)` / `.decompress(data, max_length=none)` | `LZMADecompressor` / `Bytes` | |
| `LZMADecompressor.eof` / `.needs_input` / `.unused_data` / `.check` | `bool` / `bool` / `Bytes` / `Int` | streaming state |

`lzma`, `LZMAFile`, `LZMACompressor`, and `LZMADecompressor` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/lzma.py` — namespace-only, no AST rewrite.

### zipfile + ZipFile + ZipInfo — `poop/types/zipfile.py` + `poop/transformers/zipfile.py`

`zipfile` mirrors Python's `zipfile` module — ZIP archives. Path-based construction; `With`-friendly.

| Operation | Returns | Notes |
|---|---|---|
| `ZipFile(file, mode=none, compression=none, allowZip64=true, compresslevel=none)` | `ZipFile` | default `compression=ZIP_STORED` |
| `ZipFile.read(name, pwd=none)` | `Bytes` | password is `Bytes` |
| `ZipFile.write(filename, arcname=none)` | `none` | from disk |
| `ZipFile.writestr(name, data)` | `none` | in-memory write |
| `ZipFile.extract(member, path=none, pwd=none)` | `Path` | extracted path |
| `ZipFile.extractall(path=none, members=none, pwd=none)` | `none` | members is `List[Str]` |
| `ZipFile.namelist()` | `List[Str]` | |
| `ZipFile.infolist()` | `List[ZipInfo]` | |
| `ZipFile.getinfo(name)` | `ZipInfo` | |
| `ZipFile.setpassword(pwd)` / `.close()` | `none` | |
| `ZipFile.testzip()` | `Str` / `none` | name of first bad entry, or `none` |
| `ZipInfo.filename` / `.file_size` / `.compress_size` / `.compress_type` / `.CRC` (properties) | `Str` / `Int` | |
| `ZipInfo.date_time` (property) | `Tuple(Int, Int, Int, Int, Int, Int)` | `(year, month, day, hour, minute, second)` |
| `ZipInfo.is_dir` (property) | `bool` | |
| `zipfile.ZIP_STORED` / `ZIP_DEFLATED` / `ZIP_BZIP2` / `ZIP_LZMA` (class attrs) | `Int` | |
| `zipfile.BadZipFile` / `zipfile.LargeZipFile` (class attrs) | exception classes | |
| `zipfile.is_zipfile(filename)` | `bool` | |

`zipfile`, `ZipFile`, and `ZipInfo` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/zipfile.py` — namespace-only, no AST rewrite.

### tarfile + TarFile + TarInfo — `poop/types/tarfile.py` + `poop/transformers/tarfile.py`

`tarfile` mirrors Python's `tarfile` module — TAR archives with optional gzip/bz2/lzma compression. `TarFile.open(name, mode)` is the canonical entry point; modes follow CPython (`"r:*"`, `"r:gz"`, `"w:bz2"`, `"w:xz"`, etc.).

| Operation | Returns | Notes |
|---|---|---|
| `TarFile.open(name, mode=none)` (classmethod) | `TarFile` | `mode="r"` default |
| `TarFile.is_tarfile(name)` (classmethod) | `bool` | |
| `TarFile.add(name, arcname=none, recursive=true)` | `none` | |
| `TarFile.extract(member, path=none, *, numeric_owner=false, filter=none)` | `none` | `member` is `Str` or `TarInfo` |
| `TarFile.extractall(path=none, members=none, *, numeric_owner=false, filter=none)` | `none` | safe `filter="data"` default (3.14+); members is `List[TarInfo]` |
| `TarFile.getnames()` | `List[Str]` | |
| `TarFile.getmembers()` | `List[TarInfo]` | |
| `TarFile.getmember(name)` | `TarInfo` | |
| `TarFile.list(verbose=true)` | `none` | writes to stdout |
| `TarFile.close()` | `none` | |
| `TarInfo.name` / `.linkname` / `.uname` / `.gname` (properties) | `Str` | |
| `TarInfo.size` / `.mtime` / `.mode` / `.uid` / `.gid` (properties) | `Int` | |
| `TarInfo.type` (property) | `Bytes` | tar header type byte |
| `TarInfo.is_file` / `.is_dir` / `.is_symlink` / `.is_link` (properties) | `bool` | |
| `tarfile.DEFAULT_FORMAT` / `USTAR_FORMAT` / `GNU_FORMAT` / `PAX_FORMAT` (class attrs) | `Int` | |
| `tarfile.ENCODING` (class attr) | `Str` | default encoding |
| `tarfile.data_filter` / `tar_filter` / `fully_trusted_filter` (staticmethods) | Python callables | for `filter=` argument |
| `tarfile.TarError` / `ReadError` / `CompressionError` / `StreamError` / `ExtractError` / `HeaderError` / `FilterError` / `AbsolutePathError` / `OutsideDestinationError` / `SpecialFileError` / `AbsoluteLinkError` / `LinkOutsideDestinationError` (class attrs) | exception classes | |

`tarfile`, `TarFile`, and `TarInfo` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/tarfile.py` — namespace-only, no AST rewrite.

### compression umbrella — `poop/types/compression.py` + `poop/transformers/compression.py`

`compression` mirrors Python 3.14's `compression` umbrella package — attribute access to the individual compression namespaces.

| Operation | Returns | Notes |
|---|---|---|
| `compression.zlib` / `gzip` / `bz2` / `lzma` (class attrs) | namespace classes | aliases for the standalone lowercase namespaces |

`compression.zstd` is out of scope for v1 until Python 3.14's zstandard API stabilises.

`compression` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/compression.py` — namespace-only, no AST rewrite.

### locale — `poop/types/locale.py` + `poop/transformers/locale.py`

`locale` mirrors Python's `locale` module — system locale-aware formatting and parsing. No new POOP type; the namespace exposes the standard categories, formatting helpers, and collation routines directly.

| Operation | Returns | Notes |
|---|---|---|
| `locale.getlocale(category=none)` | `Tuple(Str \| NoneClass, Str \| NoneClass)` | default `category=LC_CTYPE` |
| `locale.setlocale(category, locale=none)` | `Str` | `locale=none` queries the current setting |
| `locale.getdefaultlocale()` | `Tuple(Str \| NoneClass, Str \| NoneClass)` | deprecated upstream (3.11+) but still callable |
| `locale.getpreferredencoding(do_setlocale=none)` | `Str` | default `do_setlocale=true` |
| `locale.localeconv()` | `Dict[Str, Object]` | locale convention map |
| `locale.format_string(format, val, grouping=none, monetary=none)` | `Str` | `val` is `Int` / `Float` |
| `locale.currency(val, symbol=none, grouping=none, international=none)` | `Str` | raises `ValueError` in the C locale (no symbol) |
| `locale.str(val)` | `Str` | format a `Float` per LC_NUMERIC |
| `locale.atof(string)` | `Float` | parse a locale-formatted decimal |
| `locale.atoi(string)` | `Int` | parse a locale-formatted integer |
| `locale.delocalize(string)` | `Str` | strip locale formatting |
| `locale.normalize(localename)` | `Str` | normalize alias names |
| `locale.strcoll(s1, s2)` | `Int` | locale-aware string comparison |
| `locale.strxfrm(string)` | `Str` | comparison key for sorting |
| `locale.LC_ALL` / `LC_CTYPE` / `LC_COLLATE` / `LC_TIME` / `LC_MONETARY` / `LC_NUMERIC` / `LC_MESSAGES` (class attrs) | `Int` | category constants |
| `locale.CHAR_MAX` (class attr) | `Int` | sentinel used by `localeconv` |
| `locale.Error` (class attr) | exception class | raised by `setlocale` on unknown names |

`LC_MESSAGES` falls back to `LC_ALL` on platforms where the POSIX category is unavailable (e.g., Windows).

`locale` is exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/locale.py` — namespace-only, no AST rewrite.

### ipaddress + IPv4Address + IPv6Address + IPv4Network + IPv6Network + IPv4Interface + IPv6Interface — `poop/types/ipaddress.py` + `poop/transformers/ipaddress.py`

`ipaddress` mirrors Python's `ipaddress` module — IPv4 / IPv6 address, network, and interface objects.

| Operation | Returns | Notes |
|---|---|---|
| `IPv4Address(address)` / `IPv6Address(address)` | address | accepts `Str` / `Int` / `Bytes` / wrapper |
| `.compressed` / `.exploded` / `.reverse_pointer` (properties) | `Str` | textual forms |
| `.packed` (property) | `Bytes` | wire form |
| `.version` / `.max_prefixlen` (properties) | `Int` | |
| `.is_private` / `.is_global` / `.is_multicast` / `.is_unspecified` / `.is_reserved` / `.is_loopback` / `.is_link_local` (properties) | `Boolean` | scope predicates |
| `addr + Int(n)` / `addr - Int(n)` | address | host arithmetic |
| `addr == != < <= > >=` | as Python | ordering / equality |
| `IPv4Network(address, strict=none)` / `IPv6Network(address, strict=none)` | network | |
| `.network_address` / `.broadcast_address` / `.hostmask` / `.netmask` (properties) | address | |
| `.prefixlen` / `.num_addresses` / `.version` (properties) | `Int` | |
| `.with_prefixlen` / `.with_netmask` / `.with_hostmask` (properties) | `Str` | textual forms |
| `.hosts()` | `List[address]` | excluding network/broadcast |
| `.subnets(prefixlen_diff=none, new_prefix=none)` / `.supernet(prefixlen_diff=none, new_prefix=none)` | `List[network]` / network | |
| `.overlaps(other)` / `.subnet_of(other)` / `.supernet_of(other)` | `Boolean` | |
| `.compare_networks(other)` | `Int` | `-1` / `0` / `1` |
| `.address_exclude(network)` | `List[network]` | |
| `address in network` | `bool` | membership test |
| `IPv4Interface(address)` / `IPv6Interface(address)` | interface | `.ip` / `.network` / `.with_*` |
| `ipaddress.ip_address(address)` / `.ip_network(...)` / `.ip_interface(...)` | dispatched IPv4 or IPv6 wrapper | factory |
| `ipaddress.summarize_address_range(first, last)` | `List[network]` | minimal-cover summarization |
| `ipaddress.collapse_addresses(addresses)` | `List[network]` | dedup + merge adjacent |
| `ipaddress.get_mixed_type_key(obj)` | sortable key | helper |
| `ipaddress.AddressValueError` / `NetmaskValueError` (class attrs) | exception classes | |

`ipaddress` and all six wrapper classes are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/ipaddress.py` — namespace-only, no AST rewrite.

### urllib + Request + Response + ParseResult + SplitResult — `poop/types/urllib.py` + `poop/transformers/urllib.py`

`urllib` mirrors Python's `urllib` package — URL parsing (`urllib.parse`), HTTP fetching (`urllib.request`), and error classes (`urllib.error`). `urllib.robotparser` is out of scope for v1.

| Operation | Returns | Notes |
|---|---|---|
| `urllib.parse.urlparse(url, scheme=none, allow_fragments=none)` | `ParseResult` | `.scheme` / `.netloc` / `.path` / `.params` / `.query` / `.fragment` / `.hostname` / `.port` / `.username` / `.password` / `.geturl()` |
| `urllib.parse.urlunparse(components)` | `Str` | inverse of `urlparse` |
| `urllib.parse.urlsplit(url, scheme=none, allow_fragments=none)` | `SplitResult` | same shape as ParseResult, no `params` |
| `urllib.parse.urlunsplit(components)` | `Str` | |
| `urllib.parse.urljoin(base, url, allow_fragments=none)` | `Str` | |
| `urllib.parse.urldefrag(url)` | `Tuple(Str, Str)` | `(defragmented, fragment)` |
| `urllib.parse.quote(s, safe=none, encoding=none, errors=none)` / `.quote_plus(...)` / `.quote_from_bytes(...)` | `Str` | percent-encoding |
| `urllib.parse.unquote(s, ...)` / `.unquote_plus(...)` / `.unquote_to_bytes(...)` | `Str` / `Bytes` | decoding |
| `urllib.parse.urlencode(query, doseq=none, safe=none, encoding=none, errors=none)` | `Str` | accepts `Dict` or `List[Tuple]` |
| `urllib.parse.parse_qs(qs, keep_blank_values=none, strict_parsing=none)` | `Dict[Str, List[Str]]` | |
| `urllib.parse.parse_qsl(qs, ...)` | `List[Tuple(Str, Str)]` | preserves order |
| `Request(url, data=none, headers=none, method=none)` | `Request` | headers is `Dict[Str, Str]` |
| `Request.full_url` / `.method` / `.type` / `.host` / `.selector` (properties) | `Str` | |
| `Request.data` (property) | `Bytes` / `none` | |
| `Request.headers` (property) | `Dict[Str, Str]` | snapshot |
| `Request.add_header(key, value)` / `.add_unredirected_header(key, value)` | `none` | |
| `Request.has_header(key)` | `Boolean` | |
| `urllib.request.urlopen(url, data=none, timeout=none)` | `Response` | accepts `Str` URL or `Request` |
| `urllib.request.urlretrieve(url, filename=none, data=none)` | `Tuple(Str, Str)` | `(filename, headers_repr)` |
| `Response.status` (property) | `Int` | |
| `Response.read(size=none)` / `.readline(size=none)` | `Bytes` | |
| `Response.url` / `.reason` / `.headers` (properties) | `Str` / `Str` / `Dict` | |
| `Response.geturl()` / `.getcode()` | `Str` / `Int` | |
| `Response.close()` | `none` | `With`-friendly |
| `urllib.request.{OpenerDirector,HTTPHandler,HTTPSHandler,…}` (class attrs) | Python class refs | handler hierarchy |
| `urllib.error.URLError` / `HTTPError` / `ContentTooShortError` (class attrs) | exception classes | |

`urllib`, `Request`, `Response`, `ParseResult`, and `SplitResult` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/urllib.py` — namespace-only, no AST rewrite.

### http + HTTPStatus + HTTPMethod + HTTPConnection + HTTPSConnection + HTTPResponse + SimpleCookie + Morsel — `poop/types/http.py` + `poop/transformers/http.py`

`http` mirrors Python's `http` package — `http.client` (low-level HTTP), `http.server` (server framework), `http.cookies` (RFC 2109/6265 parsing), `http.cookiejar` (storage).

`HTTPStatus` (IntEnum) and `HTTPMethod` (StrEnum) are re-exported directly from CPython. POOP patches their `_missing_` hook so calling them with POOP `Int` / `Str` wrappers resolves to the right member (e.g. `http.HTTPStatus(Int(200))` returns `HTTPStatus.OK`).

| Operation | Returns | Notes |
|---|---|---|
| `http.HTTPStatus` (class attr) | IntEnum | `.OK` / `.NOT_FOUND` / … members; `.value` / `.phrase` / `.description` properties; `.is_success` / `.is_client_error` / `.is_server_error` / `.is_redirection` / `.is_informational` predicates |
| `http.HTTPMethod` (class attr) | StrEnum | `.GET` / `.POST` / `.PUT` / `.PATCH` / `.DELETE` / `.HEAD` / `.OPTIONS` / `.TRACE` / `.CONNECT` |
| `http.client.HTTPConnection(host, port=none, timeout=none)` | `HTTPConnection` | |
| `http.client.HTTPSConnection(host, port=none, timeout=none)` | `HTTPSConnection` | |
| `HTTPConnection.request(method, url, body=none, headers=none)` | `none` | body is `Bytes` / `Str`; headers is `Dict[Str, Str]` |
| `HTTPConnection.getresponse()` | `HTTPResponse` | |
| `HTTPConnection.set_tunnel(host, port=none, headers=none)` | `none` | proxy CONNECT |
| `HTTPConnection.close()` | `none` | |
| `HTTPResponse.status` / `.version` (properties) | `Int` | |
| `HTTPResponse.reason` (property) | `Str` | |
| `HTTPResponse.headers` (property) | `Dict[Str, Str]` | |
| `HTTPResponse.getheader(name, default=none)` | `Str` / `none` | |
| `HTTPResponse.read(amt=none)` / `.readline(limit=none)` | `Bytes` | |
| `HTTPResponse.close()` | `none` | `With`-friendly |
| `http.client.{HTTPException,BadStatusLine,InvalidURL,NotConnected,ResponseNotReady,RemoteDisconnected,UnknownProtocol}` (class attrs) | exception classes | |
| `http.client.HTTP_PORT` / `HTTPS_PORT` (class attrs) | `Int` | `80` / `443` |
| `http.server.{BaseHTTPRequestHandler,SimpleHTTPRequestHandler,CGIHTTPRequestHandler,HTTPServer,ThreadingHTTPServer}` (class attrs) | Python class refs | meant to be subclassed |
| `http.cookies.SimpleCookie(source=none)` | `SimpleCookie` | dict-of-`Morsel` |
| `SimpleCookie.load(rawdata)` / `.output(attrs=none, sep=none)` | `none` / `Str` | |
| `SimpleCookie.at(key)` / `.at_put(key, value)` / `.keys()` | `Morsel` / `none` / `List[Str]` | |
| `Morsel.key` / `.value` / `.coded_value` (properties) | `Str` | |
| `Morsel.OutputString(attrs=none)` | `Str` | |
| `http.cookies.{BaseCookie,SimpleCookie,Morsel,CookieError}` (class attrs) | classes / exceptions | |
| `http.cookiejar.{CookieJar,FileCookieJar,MozillaCookieJar,LWPCookieJar,Cookie,DefaultCookiePolicy,CookiePolicy}` (class attrs) | Python class refs | passed by reference to other networking APIs |

`http`, `HTTPConnection`, `HTTPSConnection`, `HTTPResponse`, `SimpleCookie`, and `Morsel` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/http.py` — namespace-only, no AST rewrite.

### smtplib + SMTP + SMTP_SSL + LMTP — `poop/types/smtplib.py` + `poop/transformers/smtplib.py`

`smtplib` mirrors Python's `smtplib` module — SMTP / SMTP-over-TLS / LMTP clients. The full error hierarchy and the standard port constants are exposed.

| Operation | Returns | Notes |
|---|---|---|
| `SMTP(host=none, port=none, local_hostname=none, timeout=none, source_address=none)` | `SMTP` | empty constructor defers connection |
| `SMTP_SSL(host=none, port=none, local_hostname=none, timeout=none)` | `SMTP_SSL` | TLS variant |
| `LMTP(host=none, port=none, local_hostname=none)` | `LMTP` | local MTA |
| `.connect(host=none, port=none)` | `Tuple(Int, Bytes)` | `(code, msg)` |
| `.helo(name=none)` / `.ehlo(name=none)` | `Tuple(Int, Bytes)` | |
| `.has_extn(name)` | `bool` | |
| `.starttls()` | `Tuple(Int, Bytes)` | |
| `.login(user, password)` | `Tuple(Int, Bytes)` | |
| `.sendmail(from, to, msg, mail_options=none, rcpt_options=none)` | `Dict[Str, Tuple(Int, Bytes)]` | failed recipients only |
| `.send_message(msg, from_addr=none, to_addrs=none)` | `Dict[Str, Tuple(Int, Bytes)]` | takes a Python `email.Message` |
| `.docmd(cmd, args=none)` / `.noop()` / `.verify(addr)` / `.expn(addr)` / `.rset()` | `Tuple(Int, Bytes)` | |
| `.set_debuglevel(level)` | `none` | |
| `.quit()` / `.close()` | `Tuple(Int, Bytes)` / `none` | `With`-friendly |
| `smtplib.SMTP_PORT` / `SMTP_SSL_PORT` / `LMTP_PORT` (class attrs) | `Int` | `25` / `465` / `2003` |
| `smtplib.CRLF` / `bCRLF` (class attrs) | `Str` / `Bytes` | `"\r\n"` |
| `smtplib.{SMTPException,SMTPServerDisconnected,SMTPResponseException,SMTPSenderRefused,SMTPRecipientsRefused,SMTPDataError,SMTPConnectError,SMTPHeloError,SMTPNotSupportedError,SMTPAuthenticationError}` (class attrs) | exception classes | |

`smtplib`, `SMTP`, `SMTP_SSL`, and `LMTP` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/smtplib.py` — namespace-only, no AST rewrite.

### csv + Reader + Writer + DictReader + DictWriter + Sniffer — `poop/types/csv.py` + `poop/transformers/csv.py`

`csv` mirrors Python's `csv` module — RFC 4180 reading/writing. Readers iterate from POOP `Str` (split on newlines) or `List[Str]` of lines; writers accumulate into an internal `StringIO` exposed via `.getvalue()`.

| Operation | Returns | Notes |
|---|---|---|
| `Reader(source, dialect=none, **fmtparams)` | `Reader` | source is `Str` / `List[Str]` |
| `Reader.__iter__` | yields `List[Str]` | rows |
| `Reader.line_num` / `.dialect` (properties) | `Int` / `Str` | |
| `Writer(dialect=none, **fmtparams)` | `Writer` | accumulator |
| `Writer.writerow(row)` / `.writerows(rows)` / `.getvalue()` | `Int` / `none` / `Str` | |
| `DictReader(source, fieldnames=none, restkey=none, restval=none, dialect=none, **fmtparams)` | `DictReader` | yields `Dict[Str, Str]` |
| `DictReader.fieldnames` / `.line_num` | `List[Str]` / `none` / `Int` | |
| `DictWriter(fieldnames, restval=none, extrasaction=none, dialect=none, **fmtparams)` | `DictWriter` | |
| `DictWriter.writeheader()` / `.writerow(dict)` / `.writerows(rows)` / `.getvalue()` | `Int` / `Int` / `none` / `Str` | |
| `Sniffer().sniff(sample, delimiters=none)` / `.has_header(sample)` | dialect / `Boolean` | |
| `csv.reader(...)` / `.writer(...)` | factories | aliases for the classes |
| `csv.list_dialects()` / `.get_dialect(name)` / `.register_dialect(name, dialect=none, **fmtparams)` / `.unregister_dialect(name)` | `List[Str]` / dialect / `none` / `none` | |
| `csv.field_size_limit(new_limit=none)` | `Int` | returns previous |
| `csv.Dialect` / `excel` / `excel_tab` / `unix_dialect` (class attrs) | Python class refs | |
| `csv.QUOTE_ALL` / `QUOTE_MINIMAL` / `QUOTE_NONNUMERIC` / `QUOTE_NONE` / `QUOTE_STRINGS` / `QUOTE_NOTNULL` (class attrs) | `Int` | quoting constants |
| `csv.Error` (class attr) | exception class | |

`csv`, `Reader`, `Writer`, `DictReader`, `DictWriter`, and `Sniffer` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/csv.py` — namespace-only, no AST rewrite.

### configparser + ConfigParser + RawConfigParser — `poop/types/configparser.py` + `poop/transformers/configparser.py`

`configparser` mirrors Python's `configparser` module — INI-style config files. `ConfigParser` performs string interpolation by default; `RawConfigParser` is the no-interpolation variant.

| Operation | Returns | Notes |
|---|---|---|
| `ConfigParser(defaults=none, allow_no_value=none, delimiters=none, comment_prefixes=none, inline_comment_prefixes=none, strict=none, empty_lines_in_values=none, default_section=none, interpolation=none)` | `ConfigParser` | |
| `.read(filenames, encoding=none)` | `List[Str]` | `filenames` is `Path` / `Str` / `List`; returns successfully-read paths |
| `.read_string(string, source=none)` / `.read_dict(dict, source=none)` / `.read_file(source, source_name=none)` | `none` | |
| `.sections()` / `.options(section)` | `List[Str]` | |
| `.has_section(section)` / `.has_option(section, option)` | `Boolean` | |
| `.items(section=none)` | `List[Tuple]` | with section → `List[Tuple(Str, Str)]`; without → `List[Tuple(Str, Dict)]` |
| `.get(section, option, raw=none, fallback=...)` | `Str` | |
| `.getint(section, option, raw=none, fallback=...)` | `Int` | |
| `.getfloat(section, option, raw=none, fallback=...)` | `Float` | |
| `.getboolean(section, option, raw=none, fallback=...)` | `Boolean` | |
| `.defaults()` | `Dict[Str, Str]` | |
| `.add_section(section)` / `.set(section, option, value)` | `none` | |
| `.remove_section(section)` / `.remove_option(section, option)` | `Boolean` | `true` if removed |
| `.clear()` | `none` | |
| `.write_to(path, space_around_delimiters=none)` | `none` | path-based writer |
| `.write_str(space_around_delimiters=none)` | `Str` | string capture |
| `configparser.BasicInterpolation` / `ExtendedInterpolation` (class attrs) | Python class refs | |
| `configparser.{Error,NoSectionError,DuplicateSectionError,NoOptionError,DuplicateOptionError,InterpolationError,InterpolationDepthError,InterpolationMissingOptionError,InterpolationSyntaxError,ParsingError,MissingSectionHeaderError}` (class attrs) | exception classes | |

`configparser`, `ConfigParser`, and `RawConfigParser` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/configparser.py` — namespace-only, no AST rewrite.

### pwd + Passwd, grp + Group, resource + RUsage — `poop/types/{pwd,grp,resource}.py`

Three small Unix-specific namespaces shipped together. `pwd` looks up Unix password-file entries, `grp` looks up Unix group-file entries, and `resource` queries / modifies process resource limits + rusage.

| Operation | Returns | Notes |
|---|---|---|
| `pwd.getpwuid(uid)` / `.getpwnam(name)` | `Passwd` | one record per entry |
| `pwd.getpwall()` | `List[Passwd]` | full database |
| `Passwd.pw_name` / `.pw_passwd` / `.pw_gecos` / `.pw_dir` / `.pw_shell` (properties) | `Str` | |
| `Passwd.pw_uid` / `.pw_gid` (properties) | `Int` | |
| `grp.getgrgid(gid)` / `.getgrnam(name)` | `Group` | one record per entry |
| `grp.getgrall()` | `List[Group]` | full database |
| `Group.gr_name` / `.gr_passwd` (properties) | `Str` | |
| `Group.gr_gid` (property) | `Int` | |
| `Group.gr_mem` (property) | `List[Str]` | member usernames |
| `resource.getrlimit(resource_id)` / `.setrlimit(resource_id, limits)` | `Tuple(Int, Int)` / `none` | `(soft, hard)` |
| `resource.prlimit(pid, resource_id, limits=none)` | `Tuple(Int, Int)` | Linux only |
| `resource.getrusage(who)` | `RUsage` | |
| `resource.getpagesize()` | `Int` | |
| `RUsage.ru_utime` / `.ru_stime` (properties) | `Float` | CPU time |
| `RUsage.ru_maxrss` / `.ru_ixrss` / `.ru_idrss` / `.ru_isrss` / `.ru_minflt` / `.ru_majflt` / `.ru_nswap` / `.ru_inblock` / `.ru_oublock` / `.ru_msgsnd` / `.ru_msgrcv` / `.ru_nsignals` / `.ru_nvcsw` / `.ru_nivcsw` (properties) | `Int` | per-counter |
| `resource.RLIMIT_CPU` / `RLIMIT_FSIZE` / `RLIMIT_DATA` / `RLIMIT_STACK` / `RLIMIT_CORE` / `RLIMIT_RSS` / `RLIMIT_NOFILE` / `RLIMIT_OFILE` / `RLIMIT_AS` / `RLIMIT_MEMLOCK` / `RLIMIT_VMEM` / `RLIMIT_NPROC` / `RLIMIT_SBSIZE` / `RLIMIT_SWAP` / `RLIMIT_NPTS` / `RLIMIT_LOCKS` / `RLIMIT_KQUEUES` / `RLIMIT_MSGQUEUE` / `RLIMIT_NICE` / `RLIMIT_RTPRIO` / `RLIMIT_RTTIME` / `RLIMIT_SIGPENDING` (class attrs) | `Int` / `none` | platform-specific; `none` when unavailable |
| `resource.RLIM_INFINITY` (class attr) | `Int` | sentinel |
| `resource.RUSAGE_SELF` / `RUSAGE_CHILDREN` / `RUSAGE_THREAD` / `RUSAGE_BOTH` (class attrs) | `Int` / `none` | rusage targets |
| `resource.error` (class attr) | exception class | for `Try.except_` |

`pwd`, `Passwd`, `grp`, `Group`, `resource`, and `RUsage` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{pwd,grp,resource}.py` — namespace-only, no AST rewrite. Platform-specific `RLIMIT_*` / `RUSAGE_*` constants bind to `none` on platforms where they don't exist, so user code can `is_none()`-check before calling `getrlimit`.

### sys + Stdout + Stdin, atexit, gc — `poop/types/{sys,atexit,gc}.py`

Three runtime-services namespaces shipped together. `sys` exposes a curated subset of CPython's `sys` module — introspection-heavy bits (`settrace`, `_getframe`, `monitoring`, audit hooks) are deliberately out of scope. Python attributes like `sys.argv` / `sys.platform` are POOP `@property` attributes returning POOP types — POOP code reads `sys.argv.at(0)` instead of `sys.argv[0]`. `sys.stdout` / `sys.stderr` / `sys.stdin` are properties returning `Stdout` / `Stdin` wrappers that speak POOP types. Python callables (`sys.exit`, `sys.getrecursionlimit`, `sys.setrecursionlimit`) stay as methods. `atexit` registers / unregisters shutdown callbacks (POOP `Block`s). `gc` exposes the garbage-collector control surface only — `get_objects` / `get_referrers` / `is_tracked` etc. are excluded for clashing with POOP's no-introspection rule.

| Operation | Returns | Notes |
|---|---|---|
| `sys.executable` | `Path` | |
| `sys.platform` / `sys.version` / `sys.byteorder` | `Str` | |
| `sys.version_info` | `Tuple(Int, Int, Int, Str, Int)` | `(major, minor, micro, releaselevel, serial)` |
| `sys.maxsize` (property) / `sys.getrecursionlimit()` (method) | `Int` | |
| `sys.setrecursionlimit(limit)` | `none` | |
| `sys.implementation` / `sys.flags` / `sys.float_info` / `sys.int_info` / `sys.hash_info` / `sys.thread_info` | Python object | opaque named tuples |
| `sys.modules` | `Dict[Str, module]` | snapshot at call time |
| `sys.path` | `List[Str]` | snapshot at call time |
| `sys.exit(code=none)` | raises `SystemExit` | accepts `Int` or `Str` |
| `sys.argv` | `List[Str]` | mirrors Python's `sys.argv` |
| `sys.stdout` / `sys.stderr` | `Stdout` | wraps real streams |
| `sys.stdin` | `Stdin` | wraps real stream |
| `Stdout.write(s)` | `Int` | bytes written |
| `Stdout.writeln(s=none)` / `.flush()` | `none` | |
| `Stdout.isatty()` | `Boolean` | |
| `Stdin.read(size=none)` / `.readline(size=none)` | `Str` | |
| `Stdin.readlines()` | `List[Str]` | |
| `Stdin.isatty()` | `Boolean` | iterable over lines |
| `atexit.register(func, *args, **kwargs)` | the registered callable | matches CPython contract |
| `atexit.unregister(func)` / `._run_exitfuncs()` / `._clear()` | `none` | |
| `gc.enable()` / `.disable()` / `.collect(generation=2)` | `none` / `none` / `Int` | unreachable count |
| `gc.isenabled()` | `Boolean` | |
| `gc.get_threshold()` / `.get_count()` | `Tuple(Int, Int, Int)` | |
| `gc.set_threshold(t0, t1=none, t2=none)` | `none` | |
| `gc.get_stats()` | `List[Dict]` | |
| `gc.get_debug()` / `.set_debug(flags)` | `Int` / `none` | |
| `gc.DEBUG_STATS` / `DEBUG_COLLECTABLE` / `DEBUG_UNCOLLECTABLE` / `DEBUG_SAVEALL` / `DEBUG_LEAK` (class attrs) | `Int` | |
| `gc.freeze()` / `.unfreeze()` | `none` | |
| `gc.get_freeze_count()` | `Int` | |
| `gc.callbacks` | Python `list` | mutable, shared with CPython's |

`sys`, `Stdout`, `Stdin`, `atexit`, and `gc` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{sys,atexit,gc}.py` — namespace-only, no AST rewrite. POOP lambdas auto-wrap as `Block`s, so `atexit.register(lambda: ...)` works directly.

### email + EmailMessage + EmailUtils + EmailPolicy, html + HTMLParser + Entities, xml + ET + Element + ElementTree — `poop/types/{email,html,xml}.py`

Three internet-data / markup namespaces shipped together. `email` exposes the modern `EmailMessage` API (set/get content, multipart, headers as dict-like, attachments, MIME serialization) plus `email.utils` and the preset `email.policy` constants. `html` is small: `escape` / `unescape`, the SAX-style `HTMLParser`, and the named/numeric entity maps via `Entities`. `xml` scopes v1 to `ElementTree` — `Element` / `ElementTree` / `ET.fromstring` / `tostring` / `parse` / `SubElement` / `indent`. SAX (`xml.sax`) and full minidom (`xml.dom.minidom`) are intentionally out of scope.

| Operation | Returns | Notes |
|---|---|---|
| `email.message_from_string(s, policy=none)` | `EmailMessage` | |
| `email.message_from_bytes(b, policy=none)` | `EmailMessage` | |
| `EmailMessage()` | `EmailMessage` | empty, `email.policy.default` |
| `EmailMessage.set_content(content, subtype='plain')` | `none` | accepts `Str` or `Bytes` |
| `EmailMessage.get_content()` | `Str` / `Bytes` | matches stored content type |
| `EmailMessage.add_alternative(content, subtype)` | `none` | switches to multipart |
| `EmailMessage.add_attachment(content, maintype, subtype, filename=none)` | `none` | |
| `EmailMessage.is_multipart()` | `Boolean` | |
| `EmailMessage.at(key)` / `.at_put(key, val)` | `Str` / `none` | header access |
| `EmailMessage.keys()` / `.values()` / `.items()` | `List` | |
| `EmailMessage.as_string()` / `.as_bytes()` | `Str` / `Bytes` | |
| `EmailMessage.iter_parts()` / `.iter_attachments()` | `List[EmailMessage]` | |
| `EmailMessage.get_body(preferencelist=none)` | `EmailMessage` / `none` | |
| `email.utils.parseaddr(s)` | `Tuple(Str, Str)` | `(name, addr)` |
| `email.utils.formataddr(Tuple(name, addr), charset='utf-8')` | `Str` | |
| `email.utils.getaddresses(List[Str])` | `List[Tuple(Str, Str)]` | |
| `email.utils.parsedate(s)` | `Tuple` / `none` | `none` on parse failure |
| `email.utils.formatdate(timeval=none, localtime=false, usegmt=false)` | `Str` | |
| `email.utils.make_msgid(idstring=none, domain=none)` | `Str` | |
| `email.policy.default` / `.SMTP` / `.SMTPUTF8` / `.HTTP` / `.strict` / `.compat32` | Python policy obj | |
| `html.escape(s, quote=true)` / `.unescape(s)` | `Str` | |
| `html.has_entity(name)` | `Boolean` | |
| `html.entities.name2codepoint()` | `Dict[Str, Int]` | |
| `html.entities.codepoint2name()` | `Dict[Int, Str]` | |
| `html.entities.entitydefs()` / `.html5()` | `Dict[Str, Str]` | |
| `HTMLParser(convert_charrefs=true)` | `HTMLParser` | SAX-style |
| `HTMLParser.feed(data)` / `.close()` / `.reset()` | `none` | |
| `HTMLParser.getpos()` | `Tuple(Int, Int)` | `(line, offset)` |
| `HTMLParser.get_starttag_text()` | `Str` / `none` | |
| `ET.fromstring(text)` / `.XML(text)` | `Element` | |
| `ET.parse(path)` | `ElementTree` | |
| `ET.tostring(element, encoding=none)` | `Str` / `Bytes` | `none`/`"unicode"` → `Str` |
| `ET.SubElement(parent, tag, attrib=none)` | `Element` | |
| `ET.indent(tree, space="  ")` | `none` | |
| `ET.ParseError` (class attr) | exception class | |
| `Element(tag, attrib=none)` | `Element` | |
| `Element.tag` / `.text` / `.tail` / `.attrib` (properties) | `Str` / `Dict` | text/tail may be `none`; `.text` / `.tail` writable via assignment |
| `Element.get(key, default=none)` / `.set(key, val)` | `Str` / `none` / `none` | |
| `Element.keys()` / `.items()` | `List` | |
| `Element.append(child)` / `.extend(children)` / `.insert(i, child)` / `.remove(child)` / `.clear()` | `none` | |
| `Element.find(path)` / `.findall(path)` / `.iterfind(path)` | `Element` / `none` / `List` | |
| `Element.findtext(path, default=none)` | `Str` / `none` | |
| `Element.iter(tag=none)` / `.itertext()` | `List[Element]` / `List[Str]` | |
| `Element.len()` | `Int` | child count |
| `ElementTree(element=none)` / `.getroot()` | `ElementTree` / `Element` or `none` | |
| `ElementTree.write(path, encoding=none)` | `none` | |
| `ElementTree.find/findall/findtext/iter` | (same as `Element`) | |

`email`/`EmailMessage`/`html`/`HTMLParser`/`xml`/`ET`/`Element`/`ElementTree` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{email,html,xml}.py` — namespace-only, no AST rewrite. `xml.etree` uses `xml.etree.ElementTree` directly (suppressed `S314` ruff hints) — users with XXE concerns can swap to `defusedxml` themselves; POOP's transformers do not load external DTDs by default but does not actively block them either.

### unittest + TestCase + TestSuite + TestRunner + TestResult, cProfile + Profile + pstats + Stats + SortKey, timeit + Timer — `poop/types/{unittest,profile,timeit}.py`

Three dev / debug / profile namespaces shipped together. `unittest` is a POOP-flavoured re-implementation of the canonical xUnit surface (the full `unittest.TestCase` would drag in subprocess-style runner internals — POOP keeps the assertions + lightweight runner). `cProfile.Profile` and `pstats.Stats` wrap their Python counterparts directly; the namespaces expose `cProfile.run`, the `Profile` class (works as a context manager via `With`), and the `Stats` aggregator. `timeit` is straightforward — module-level `timeit`/`repeat`/`default_timer` plus a `Timer` class.

| Operation | Returns | Notes |
|---|---|---|
| `TestCase()` | `TestCase` | subclass to add `test_*` methods |
| `TestCase.setUp()` / `.tearDown()` | overridable | hooks |
| `TestCase.assertEqual/NotEqual/True/False/Is/IsNot/IsNone/IsNotNone(...)` | raises `AssertionError` on failure | |
| `TestCase.assertIsInstance/NotIsInstance(x, cls, msg=none)` | raises on failure | |
| `TestCase.assertGreater/GreaterEqual/Less/LessEqual(a, b, msg=none)` | raises on failure | |
| `TestCase.assertAlmostEqual(a, b, places=7, msg=none)` | raises on failure | |
| `TestCase.assertRaises(exc, callable, *args, **kwargs)` | raises if no exception thrown | |
| `TestCase.fail(msg=none)` / `.skipTest(reason)` | raises `AssertionError` / `SkipTest` | |
| `TestCase.run_method(method_name)` | `TestResult` | run a single test method |
| `TestSuite()` / `.addTest(case, method_name)` / `.countTestCases()` / `.run()` | `TestSuite` / `none` / `Int` / `TestResult` | |
| `TestRunner().run(suite)` | `TestResult` | |
| `TestResult.testsRun` (property) | `Int` | |
| `TestResult.wasSuccessful()` | `Boolean` | |
| `TestResult.failure_count()` / `.error_count()` / `.skipped_count()` | `Int` | |
| `unittest.skip(reason)` / `.skipIf(cond, reason)` / `.skipUnless(cond, reason)` / `.expectedFailure(func)` | decorators | |
| `unittest.SkipTest` (class attr) | exception class | for `Try.except_` |
| `cProfile.run(command, filename=none)` | `none` | |
| `Profile()` | `Profile` | `With(Profile())` for scoped capture |
| `Profile.enable()` / `.disable()` / `.create_stats()` / `.dump_stats(path)` | `none` | |
| `Profile.print_stats()` | `Str` | captured stdout |
| `Profile.runcall(func, *args, **kwargs)` | function's result | |
| `Stats(source)` | `Stats` | source: `Profile` / `Str` (filename) / `Path` |
| `Stats.sort_stats(*keys)` / `.reverse_order()` / `.strip_dirs()` | `Stats` | chainable |
| `Stats.print_stats()` / `.print_callers()` / `.print_callees()` | `Str` | captured |
| `Stats.add(*sources)` | `Stats` | merge additional profile data |
| `Stats.dump_stats(path)` | `none` | |
| `SortKey.CALLS` / `.CUMULATIVE` / `.FILENAME` / `.LINE` / `.NAME` / `.NFL` / `.PCALLS` / `.STDNAME` / `.TIME` (class attrs) | `Str` | |
| `timeit.timeit(stmt, setup, number=1_000_000)` | `Float` | |
| `timeit.repeat(stmt, setup, repeat=5, number=1_000_000)` | `List[Float]` | |
| `timeit.default_timer()` | `Float` | current time from `time.perf_counter` |
| `Timer(stmt, setup, timer=none)` / `.timeit(number)` / `.repeat(repeat, number)` / `.autorange()` | `Timer` / `Float` / `List[Float]` / `Tuple(Int, Float)` | |

`unittest`/`TestCase`/`TestSuite`/`TestRunner`/`TestResult`/`cProfile`/`profile` (alias)/`Profile`/`pstats`/`Stats`/`SortKey`/`timeit`/`Timer` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{unittest,profile,timeit}.py` — namespace-only, no AST rewrite. The full mock surface (`unittest.mock` / `MagicMock` / `patch`) is out of scope for v1.

### signal, socket + Socket, ssl + SSLContext, asyncio + Future — `poop/types/{signal,socket,ssl,asyncio}.py`

Four networking namespaces shipped together. `signal` wraps OS signal registration and exposes the standard signal constants (platform-specific ones bind to `none` when unavailable). `socket` mirrors CPython's `socket.socket` as the POOP `Socket` class plus the module-level helpers (`gethostbyname`, `inet_aton`, `create_connection`/`create_server`, …). `ssl` wraps `SSLContext` and the standard verify / protocol constants. `asyncio` exposes `run`, `sleep`, `gather`, `wait_for`, `shield`, `create_task`, and `Future`. POOP source can write `async def` methods and `await` directly (since v0.52.0) — `AsyncIO.run(some_method())` is the canonical entry point.

| Operation | Returns | Notes |
|---|---|---|
| `signal.signal(num, handler)` | previous handler | `handler` accepts a POOP `Block` routed through `block.bridge`, or the sentinels `Signal.SIG_DFL` / `SIG_IGN` |
| `signal.getsignal(num)` | handler | |
| `signal.strsignal(num)` | `Str` / `none` | |
| `signal.raise_signal(num)` / `.pthread_kill(tid, num)` | `none` | |
| `signal.sigpending()` | `Set[Int]` | |
| `signal.siginterrupt(num, flag)` | `none` | toggle whether the syscall restarts after the signal |
| `signal.sigwait(sigset)` | `Int` | block until one of the signals in `sigset` is delivered |
| `signal.pthread_sigmask(how, mask)` | `Set[Int]` | POSIX-only; uses `SIG_BLOCK` / `SIG_UNBLOCK` / `SIG_SETMASK` |
| `signal.sigwaitinfo(sigset)` / `.sigtimedwait(sigset, timeout)` | `Dict[Str, Int]` | siginfo flattened to a dict; `sigtimedwait` returns `none` on timeout |
| `signal.SIG_BLOCK` / `SIG_UNBLOCK` / `SIG_SETMASK` (class attrs) | `Int` or `none` | POSIX-only; `none` on Windows |
| `signal.SIG_DFL` / `.SIG_IGN` (class attrs) | sentinel | |
| `signal.SIGABRT` / `SIGINT` / `SIGTERM` / … (class attrs) | `Int` / `none` | platform-specific |
| `signal.ITIMER_REAL` / `ITIMER_VIRTUAL` / `ITIMER_PROF` (class attrs) | `Int` / `none` | Unix only |
| `Socket(family=AF_INET, type=SOCK_STREAM, proto=0)` | `Socket` | also via `with Socket() as s:` |
| `Socket.bind(addr)` / `.listen(backlog=none)` / `.connect(addr)` / `.shutdown(how)` / `.close()` | `none` | |
| `Socket.accept()` | `Tuple(Socket, Address)` | |
| `Socket.connect_ex(addr)` | `Int` | error code |
| `Socket.send(data)` / `.sendto(data, addr)` | `Int` | bytes sent |
| `Socket.sendall(data)` | `none` | |
| `Socket.recv(bufsize)` | `Bytes` | |
| `Socket.recvfrom(bufsize)` | `Tuple(Bytes, Address)` | |
| `Socket.setsockopt(level, opt, value)` / `.getsockopt(level, opt)` | `none` / `Int` | |
| `Socket.settimeout(value)` / `.gettimeout()` | `none` / `Float` or `none` | |
| `Socket.setblocking(flag)` | `none` | |
| `Socket.fileno()` | `Int` | |
| `Socket.getsockname()` / `.getpeername()` | `Tuple` | address |
| `socket.gethostname()` / `.gethostbyname(host)` / `.getfqdn(...)` | `Str` | |
| `socket.gethostbyname_ex(host)` / `.gethostbyaddr(addr)` | `Tuple(Str, List, List)` | |
| `socket.getservbyname(name, proto=none)` / `.getservbyport(port, proto=none)` | `Int` / `Str` | |
| `socket.htons/htonl/ntohs/ntohl(x)` | `Int` | |
| `socket.inet_aton/ntoa(...)` / `.inet_pton/ntop(family, ...)` | `Bytes` / `Str` | |
| `socket.create_connection(addr, timeout=none)` / `.create_server(addr, family=none)` | `Socket` | |
| `socket.has_dualstack_ipv6()` | `Boolean` | |
| `socket.getaddrinfo(host, port, family=none, type=none, proto=none, flags=none)` | `List[Tuple(family, type, proto, canonname, sockaddr)]` | `host`/`port` may be `none` |
| `socket.getnameinfo(sockaddr, flags)` | `Tuple(Str, Str)` | `(host, port)` |
| `socket.if_indextoname(idx)` / `.if_nametoindex(name)` / `.if_nameindex()` | `Str` / `Int` / `List[Tuple(Int, Str)]` | network-interface enumeration |
| `socket.SocketType` (class attr) | underlying `_socket.socket` type | exposed for compat with `isinstance` checks against legacy code |
| `socket.AF_INET` / `AF_INET6` / `AF_UNSPEC` / `AF_UNIX` / `SOCK_STREAM` / `SOCK_DGRAM` / `SOCK_RAW` / `SOL_SOCKET` / `SO_REUSEADDR` / `SO_KEEPALIVE` / `SO_BROADCAST` / `SHUT_RD` / `SHUT_WR` / `SHUT_RDWR` / `AI_*` / `NI_*` (class attrs) | `Int` | platform-specific (`AF_UNIX` may be `none`) |
| `socket.error` / `.herror` / `.gaierror` / `.timeout` (class attrs) | exception class | for `Try.except_` |
| `ssl.create_default_context(cafile=none, capath=none)` | `SSLContext` | |
| `SSLContext()` / `.load_cert_chain(certfile, keyfile=none, password=none)` / `.load_verify_locations(...)` / `.load_default_certs()` | `SSLContext` / `none` | |
| `SSLContext.set_ciphers(ciphers)` / `.get_ciphers()` | `none` / Python list | |
| `SSLContext.verify_mode` / `.check_hostname` (properties) | `Int` / `Boolean` | writable via assignment |
| `SSLContext.wrap_socket(sock, server_hostname=none, server_side=none)` | `Socket` | |
| `ssl.PROTOCOL_TLS_CLIENT` / `PROTOCOL_TLS_SERVER` / `CERT_NONE` / `CERT_OPTIONAL` / `CERT_REQUIRED` (class attrs) | `Int` | |
| `ssl.SSLError` / `SSLZeroReturnError` / `SSLWantReadError` / `SSLWantWriteError` / `SSLSyscallError` / `SSLEOFError` / `SSLCertVerificationError` (class attrs) | exception class | |
| `asyncio.run(coro, debug=none)` | result | accepts coroutine or zero-arg callable |
| `asyncio.sleep(delay, result=none)` | awaitable | |
| `asyncio.gather(*coros)` | awaitable | resolves to list of results |
| `asyncio.wait_for(coro, timeout=none)` / `.shield(coro)` | awaitable | |
| `asyncio.create_task(coro)` / `.ensure_future(coro)` | `Future` | requires running loop |
| `asyncio.new_event_loop()` / `.set_event_loop(loop)` / `.get_event_loop()` | Python loop / `none` | |
| `Future.done()` / `.cancelled()` | `Boolean` | |
| `Future.result()` / `.exception()` | underlying value / exception | |
| `Future.cancel()` | `Boolean` | |
| `asyncio.CancelledError` / `TimeoutError` / `InvalidStateError` / `IncompleteReadError` (class attrs) | exception class | |

`signal`/`socket`/`Socket`/`ssl`/`SSLContext`/`asyncio`/`Future` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{signal,socket,ssl,asyncio}.py` — namespace-only, no AST rewrite. POOP code can define coroutines directly as `async def` methods on a class and `await` other coroutines; the namespace is also fully reachable when POOP code is interoperating with an existing async Python library. `async for` / `async with` / async generators remain forbidden (by `no_loops`, `no_with`, and `no_yield` respectively).

### os + Environ, io + StringIO + BytesIO, time + StructTime, logging + Logger + Handler + Formatter, platform + Uname — `poop/types/{os,io,time,logging,platform}.py`

Five generic-OS namespaces shipped together. `os` mirrors Python's `os` module shape directly: process-state queries (`getpid`/`getppid`/`getuid`/`getgid`/`geteuid`/`getegid`/`umask`/`chdir`/`getcwd`/`kill`), random bytes (`urandom`), CPU counts (`cpu_count`/`process_cpu_count`/`getloadavg`), and the low-level flag/separator constants. The `os.environ` sub-namespace handles environment variables — since POOP forbids subscript syntax, Python's `os.environ["X"] = "y"` becomes the explicit `os.environ.set("X", "y")`. `os.path` is **intentionally absent** — every operation is reachable via `Path`. `io` exposes the in-memory buffers `StringIO` / `BytesIO` plus the seek constants — disk I/O still goes through `Path.read_*` / `write_*`. `time` mirrors the wall-clock / monotonic / perf-counter / process-time / thread-time API plus parse/format helpers; `StructTime` wraps `time.struct_time`. `logging` exposes the canonical xUnit-style framework (Logger + Handler + Formatter) — `logging.config` and `logging.handlers` are out of scope for v1. `platform` returns runtime environment info and exposes `Uname` as a POOP record.

| Operation | Returns | Notes |
|---|---|---|
| `os.urandom(n)` | `Bytes` | |
| `os.cpu_count()` / `.process_cpu_count()` | `Int` / `none` | |
| `os.getloadavg()` | `Tuple(Float, Float, Float)` | Unix only |
| `os.F_OK` / `R_OK` / `W_OK` / `X_OK` / `O_RDONLY` / `O_WRONLY` / `O_RDWR` / `O_APPEND` / `O_CREAT` / `O_TRUNC` / `O_EXCL` (class attrs) | `Int` | |
| `os.sep` / `linesep` / `pathsep` / `devnull` (class attrs) | `Str` | |
| `os.getpid()` / `.getppid()` / `.getuid()` / `.getgid()` / `.geteuid()` / `.getegid()` | `Int` | |
| `os.umask(m)` | `Int` | previous mask |
| `os.chmod(path, mode, follow_symlinks=true)` | `none` | path-mode permission bits |
| `os.chown(path, uid, gid, follow_symlinks=true)` | `none` | path ownership |
| `os.chdir(p)` / `.kill(pid, sig)` | `none` | |
| `os.getcwd()` | `Path` | |
| `os.walk(top, topdown=true, onerror=none, followlinks=false)` | `List[Tuple(Path, List[Str], List[Str])]` | eager; `onerror` accepts a `Block` routed through `block.bridge` |
| `os.environ.get(key, default=none)` | `Str` / `none` | |
| `os.environ.set(key, value)` / `.unset(key)` | `none` | mutators (replace Python's `environ[k]=v` / `del environ[k]`) |
| `os.environ.has(key)` | `Boolean` | |
| `os.environ.keys()` | `Set[Str]` | |
| `os.environ.values()` | `List[Str]` | |
| `os.environ.as_dict()` | `Dict[Str, Str]` | snapshot |
| `StringIO(initial='', newline=none)` / `BytesIO(initial=b'')` | buffer | works as `With` ctx mgr |
| `StringIO.read(size=none)` / `.readline(size=none)` / `.getvalue()` | `Str` | |
| `BytesIO.read(size=none)` / `.readline(size=none)` / `.getvalue()` | `Bytes` | |
| `StringIO/BytesIO.write(x)` / `.seek(p, w=none)` / `.tell()` / `.truncate(s=none)` | `Int` | |
| `StringIO/BytesIO.close()` | `none` | |
| `io.SEEK_SET` / `SEEK_CUR` / `SEEK_END` / `DEFAULT_BUFFER_SIZE` (class attrs) | `Int` | |
| `io.UnsupportedOperation` / `BlockingIOError` (class attrs) | exception class | |
| `time.time()` / `.monotonic()` / `.perf_counter()` / `.process_time()` / `.thread_time()` | `Float` | seconds |
| `time.time_ns()` / `.monotonic_ns()` / `.perf_counter_ns()` / `.process_time_ns()` / `.thread_time_ns()` | `Int` | nanoseconds |
| `time.sleep(seconds)` | `none` | |
| `time.strftime(fmt, t=none)` / `.asctime(t=none)` / `.ctime(secs=none)` | `Str` | |
| `time.strptime(s, fmt)` / `.gmtime(secs=none)` / `.localtime(secs=none)` | `StructTime` | |
| `time.mktime(t)` | `Float` | |
| `time.tzname` | `Tuple(Str, Str)` | |
| `time.timezone` / `time.altzone` / `time.daylight` | `Int` | |
| `time.CLOCK_REALTIME` / `CLOCK_MONOTONIC` / `CLOCK_MONOTONIC_RAW` / `CLOCK_PROCESS_CPUTIME_ID` / `CLOCK_THREAD_CPUTIME_ID` / `CLOCK_BOOTTIME` (class attrs) | `Int` or `none` | POSIX clock IDs; `none` on platforms without the helper |
| `time.clock_gettime(id)` / `.clock_getres(id)` | `Float` | POSIX clock read |
| `time.clock_gettime_ns(id)` | `Int` | nanosecond precision read |
| `time.clock_settime(id, t)` / `.clock_settime_ns(id, t)` | `none` | privileged write (typically `CLOCK_REALTIME` only) |
| `StructTime.tm_year` / `tm_mon` / `tm_mday` / `tm_hour` / `tm_min` / `tm_sec` / `tm_wday` / `tm_yday` / `tm_isdst` (properties) | `Int` | |
| `StructTime.tm_zone` / `tm_gmtoff` (properties) | `Str` or `none` / `Int` or `none` | |
| `logging.getLogger(name=none)` | `Logger` | |
| `logging.basicConfig(*, filename=none, filemode=none, format=none, datefmt=none, style=none, level=none, handlers=none, force=false, encoding=none, errors=none)` | `none` | `filename` is a POOP `Path`; `stream` omitted (no file-object abstraction) |
| `logging.debug/info/warning/error/critical(msg)` / `.log(level, msg)` | `none` | root logger shortcuts |
| `logging.getLevelName(level)` / `.addLevelName(level, name)` | `Str` / `none` | |
| `logging.StreamHandler()` / `.NullHandler()` / `.FileHandler(path)` | `Handler` | |
| `logging.CRITICAL` / `ERROR` / `WARNING` / `INFO` / `DEBUG` / `NOTSET` (class attrs) | `Int` | |
| `Logger.setLevel(l)` / `.addHandler(h)` / `.removeHandler(h)` | `none` | |
| `Logger.getEffectiveLevel()` | `Int` | |
| `Logger.isEnabledFor(level)` / `.propagate` (property) | `Boolean` | `.propagate` writable via assignment |
| `Logger.debug/info/warning/error/critical/exception(msg)` / `.log(level, msg)` | `none` | |
| `Logger.handlers()` | `List[Handler]` | |
| `Handler.setLevel(l)` / `.setFormatter(f)` / `.addFilter(f)` / `.removeFilter(f)` | `none` | |
| `Formatter(fmt=none, datefmt=none, style=none, validate=true, defaults=none)` | `Formatter` | |
| `Filter(name=none)` | `Filter` | |
| Subclass `Filter` / `Handler` / `Formatter` and override `filter(record)` / `emit(record)` / `format(record)` | — | overrides routed through `block.bridge`; override receives the raw `_logging.LogRecord`, wrap it in `LogRecord(record)` for POOP-typed fields |
| `LogRecord(record)` exposes `.name` / `.msg` / `.args` / `.levelname` / `.levelno` / `.pathname` / `.filename` / `.module` / `.lineno` / `.funcName` / `.created` / `.thread` / `.threadName` / `.process` / `.processName` (properties) and `.getMessage()` | POOP types | wraps `_logging.LogRecord` for handler/formatter overrides |
| `LoggerAdapter(logger, extra=none)` plus `.debug` / `.info` / `.warning` / `.error` / `.critical` / `.log` / `.setLevel` | `LoggerAdapter` / `none` | passes `extra` through every log call |
| `BufferingFormatter(linefmt=none)` | `BufferingFormatter` | header/footer-aware batch formatter |
| `Logging.Filterer` / `PercentStyle` / `StrFormatStyle` / `StringTemplateStyle` (class attrs) | raw stdlib class refs | exposed for `isinstance` checks |
| `logging.exception(msg)` / `.disable(level=none)` / `.captureWarnings(flag)` / `.makeLogRecord(d)` | `none` / `LogRecord` | module-level helpers |
| `logging.getHandlerByName(name)` / `.getHandlerNames()` / `.getLevelNamesMapping()` | `Handler` or `none` / `List[Str]` / `Dict[Str, Int]` | introspection |
| `logging.getLogRecordFactory()` / `.setLogRecordFactory(f)` / `.getLoggerClass()` / `.setLoggerClass(c)` | raw Python callable/type | factory/class hooks |
| `logging.dictConfig(d)` / `.fileConfig(path, defaults=none, disable_existing_loggers=true, encoding=none)` | `none` | mirror of `logging.config.dictConfig` / `fileConfig` |
| `logging.raiseExceptions` / `logThreads` / `logProcesses` / `logMultiprocessing` / `logAsyncioTasks` (class properties) | `Boolean` | writable; updates the underlying `_logging` module attribute |
| `platform.system()` / `.release()` / `.version()` / `.machine()` / `.processor()` / `.node()` / `.platform(...)` | `Str` | |
| `platform.uname()` | `Uname` | |
| `platform.architecture()` | `Tuple(Str, Str)` | `(bits, linkage)` |
| `platform.python_version()` / `.python_branch()` / `.python_compiler()` / `.python_implementation()` / `.python_revision()` | `Str` | |
| `platform.python_version_tuple()` / `.python_build()` / `.libc_ver()` | `Tuple[Str, ...]` | |
| `platform.mac_ver()` / `.win32_ver()` | `Tuple` | per-OS specifics |
| `Uname.system` / `.node` / `.release` / `.version` / `.machine` / `.processor` (properties) | `Str` | |

`os`/`io`/`StringIO`/`BytesIO`/`time`/`StructTime`/`logging`/`Logger`/`Handler`/`Formatter`/`platform`/`Uname` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{os,io,time,logging,platform}.py` — namespace-only, no AST rewrite. The `Environ` sub-namespace is reachable via `os.environ` rather than the top-level (mirroring Python's `os.environ` attribute). The pure-Python `os.path` family is **intentionally absent** — every operation is reachable via `Path` (POOP's `pathlib.Path` mirror). Likewise, `io.open` is replaced by `Path.read_text` / `write_text` / `read_bytes` / `write_bytes`. `logging.config` (file/dict configuration) and `logging.handlers` (rotating, SMTP, syslog) are out of scope for v1.

### threading + Thread + Lock/RLock + Event + Semaphore + Barrier, multiprocessing + Process + MPQueue + Pool, concurrent + ThreadPoolExecutor + ProcessPoolExecutor + CFFuture, subprocess + Popen + CompletedProcess, queue + Queue + LifoQueue + PriorityQueue + SimpleQueue — `poop/types/{threading,multiprocessing,concurrent,subprocess,queue}.py`

Five concurrent-execution namespaces shipped together. `threading` exposes `Thread` + the synchronisation primitives (`Lock`/`RLock`/`Event`/`Semaphore`/`Barrier`) — all primitives are `With`-friendly. `multiprocessing` mirrors the structure for cross-process execution: `Process` + `MPQueue` + `Pool` plus the module helpers. `concurrent.futures` exposes `ThreadPoolExecutor` + `ProcessPoolExecutor` + `CFFuture` (named to disambiguate from `asyncio.Future`). `subprocess` is the canonical shell-out API: high-level `run` (returning `CompletedProcess`), the backward-compat `call`/`check_call`/`check_output`/`getoutput`/`getstatusoutput`, and the full-lifecycle `Popen`. `queue` provides synchronised FIFO/LIFO/priority/simple queues.

| Operation | Returns | Notes |
|---|---|---|
| `Thread(target=none, name=none, daemon=none)` | `Thread` | |
| `Thread.start()` / `.join(timeout=none)` | `none` | |
| `Thread.is_alive()` | `Boolean` | |
| `Thread.name` / `.ident` / `.native_id` / `.daemon` (properties) | `Str` / `Int` or `none` / `Boolean` | |
| `Lock()` / `RLock()` / `Event()` / `Semaphore(v=1)` / `Barrier(parties, timeout=none)` | primitive | each `With`-friendly |
| `Lock/RLock.acquire(blocking=true, timeout=none)` / `.release()` | `Boolean` / `none` | |
| `Lock.locked()` | `Boolean` | |
| `Event.set()` / `.clear()` / `.is_set()` / `.wait(timeout=none)` | `none` / `Boolean` | |
| `Semaphore.acquire(...)` / `.release()` | `Boolean` / `none` | |
| `Barrier.wait(timeout=none)` / `.reset()` / `.abort()` | `Int` / `none` | |
| `Barrier.parties` / `.n_waiting` / `.broken` (properties) | `Int` / `Boolean` | |
| `threading.current_thread()` / `.main_thread()` | `Thread` | |
| `threading.active_count()` / `.get_ident()` / `.get_native_id()` | `Int` | |
| `threading.enumerate()` | `List[Thread]` | |
| `threading.BrokenBarrierError` (class attr) | exception class | |
| `multiprocessing.Process(target=none, name=none, daemon=none)` | `Process` | same shape as `Thread` |
| `Process.start()` / `.join` / `.is_alive` / `.terminate` / `.kill` / `.close` | `none` / `Boolean` / `none` | |
| `Process.pid` / `.exitcode` / `.name` (properties) | `Int` or `none` / `Str` | |
| `MPQueue(maxsize=none)` / `.put` / `.get` / `.qsize` / `.empty` / `.full` / `.close` | typed | mirror `queue.Queue` |
| `Pool(processes=none)` / `.apply(fn, args=none)` / `.map(fn, iter)` / `.close` / `.terminate` / `.join` | typed | `With`-friendly |
| `multiprocessing.cpu_count()` | `Int` | |
| `multiprocessing.active_children()` | `List[Process]` | |
| `multiprocessing.current_process()` | `Process` | |
| `multiprocessing.get_start_method(allow_none=none)` | `Str` or `none` | |
| `ThreadPoolExecutor(max_workers=none, thread_name_prefix=none)` / `ProcessPoolExecutor(max_workers=none)` | executor | `With`-friendly |
| `Executor.submit(fn, *args, **kwargs)` | `CFFuture` | |
| `Executor.map(fn, iterable)` | `List` | results materialised |
| `Executor.shutdown(wait=true, cancel_futures=false)` | `none` | |
| `CFFuture.result(timeout=none)` / `.exception(timeout=none)` | underlying value / exception or `none` | |
| `CFFuture.cancel()` / `.cancelled()` / `.done()` / `.running()` | `Boolean` | |
| `concurrent.wait(futures, timeout=none, return_when=none)` | `Tuple(List, List)` | done / not-done |
| `concurrent.as_completed(futures, timeout=none)` | `List[CFFuture]` | |
| `concurrent.FIRST_COMPLETED` / `FIRST_EXCEPTION` / `ALL_COMPLETED` (class attrs) | `Str` | |
| `concurrent.CancelledError` / `TimeoutError` / `BrokenExecutor` / `InvalidStateError` (class attrs) | exception class | |
| `subprocess.run(args, capture_output=none, check=none, shell=none, cwd=none, timeout=none, text=none, input=none)` | `CompletedProcess` | |
| `subprocess.call(args, shell=none)` / `.check_call(args, shell=none)` | `Int` | |
| `subprocess.check_output(args, shell=none, text=none)` | `Bytes` or `Str` | |
| `subprocess.getoutput(cmd)` | `Str` | |
| `subprocess.getstatusoutput(cmd)` | `Tuple(Int, Str)` | |
| `CompletedProcess.returncode` / `.args` / `.stdout` / `.stderr` (properties) | `Int` / Python args / `Str`/`Bytes` or `none` | |
| `CompletedProcess.check_returncode()` | `none` | raises on non-zero |
| `Popen(args, **kwargs)` | `Popen` | accepts native Python kwargs |
| `Popen.wait(timeout=none)` / `.poll()` / `.terminate()` / `.kill()` / `.send_signal(sig)` | `Int` / `Int` or `none` / `none` | |
| `Popen.communicate(input=none, timeout=none)` | `Tuple(Str/Bytes/none, Str/Bytes/none)` | |
| `Popen.pid` / `.returncode` (properties) | `Int` / `Int` or `none` | |
| `subprocess.PIPE` / `STDOUT` / `DEVNULL` (class attrs) | `Int` | |
| `subprocess.SubprocessError` / `CalledProcessError` / `TimeoutExpired` (class attrs) | exception class | |
| `Queue(maxsize=none)` / `LifoQueue(maxsize=none)` / `PriorityQueue(maxsize=none)` / `SimpleQueue()` | queue | |
| `Queue.put(item, block=true, timeout=none)` / `.get(...)` / `.put_nowait` / `.get_nowait` / `.qsize` / `.empty` / `.full` | typed | |
| `Queue.task_done()` / `.join()` | `none` | LifoQueue/PriorityQueue also expose these |
| `queue.Empty` / `Full` (class attrs) | exception class | |

`threading`/`Thread`/`Lock`/`RLock`/`Event`/`Semaphore`/`Barrier`/`multiprocessing`/`Pool`/`MPQueue`/`concurrent`/`ThreadPoolExecutor`/`ProcessPoolExecutor`/`CFFuture`/`subprocess`/`Popen`/`CompletedProcess`/`queue`/`Queue`/`LifoQueue`/`PriorityQueue`/`SimpleQueue` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{threading,multiprocessing,concurrent,subprocess,queue}.py` — namespace-only, no AST rewrite. `multiprocessing.Process` is **only reachable via `multiprocessing.Process`** (not bound as a top-level name) — that matches Python's idiomatic usage and avoids ambiguity with future `Process`-named types. POOP's `Block` (lambda-wrapping) does not pickle across the `multiprocessing` boundary on `forkserver` start methods — module-level Python functions must be used as `target=...` for `Process` / `Pool` workers.

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


## Stdlib coverage

Per-module audit of `sys.stdlib_module_names` (194 top-level modules, private `_*` modules excluded) grouped by the [docs.python.org/3/library](https://docs.python.org/3/library/) categories. Each row is annotated with one of:

- **covered** — already reachable from POOP today.
- **out** — won't be surfaced; reason in the sketch column.

Every newly-wrapped or intentionally-skipped module should land here in the same commit that adds (or skips) it.


### Text Processing Services

| Module | Status | Sketch |
|---|---|---|
| `string` | covered | `string` + `Template` (shipped in v0.34.0) |
| `re` | covered | `re` + `Pattern` + `Match` (shipped in v0.29.0) |
| `difflib` | covered | `difflib` + `SequenceMatcher` (shipped in v0.34.0) |
| `textwrap` | covered | `textwrap` + `TextWrapper` (shipped in v0.34.0) |
| `unicodedata` | covered | `unicodedata` namespace (shipped in v0.34.0) |
| `stringprep` | out | Internal IDNA helper |
| `readline` | out | REPL infrastructure — POOP doesn't expose a REPL |
| `rlcompleter` | out | REPL infrastructure |

### Binary Data Services

| Module | Status | Sketch |
|---|---|---|
| `struct` | covered | `struct` + `Struct` (shipped in v0.37.0) |
| `codecs` | covered | `codecs` + `CodecInfo` (shipped in v0.37.0) |

### Data Types

| Module | Status | Sketch |
|---|---|---|
| `datetime` | covered | `datetime` + `Date` + `Time` + `DateTime` + `TimeDelta` + `TimeZone` (shipped in v0.32.0) |
| `zoneinfo` | covered | `zoneinfo` + `ZoneInfo` (shipped in v0.35.0) |
| `calendar` | covered | `calendar` + `Calendar` (shipped in v0.35.0) |
| `collections` | covered | `OrderedDict` / `Counter` / `deque` redundant — POOP collections carry the methods |
| `heapq` | covered | `heapq` namespace + `HeapMerge` (shipped in v0.22.0) |
| `bisect` | covered | `bisect` namespace (shipped in v0.21.0) |
| `array` | covered | `array` + `Array` (shipped in v0.35.0) |
| `weakref` | covered | `weakref` + `WeakRef` + `WeakSet` + `WeakKeyDictionary` + `WeakValueDictionary` (shipped in v0.35.0) |
| `types` | out | Introspection — forbidden in POOP |
| `copy` | covered | `copy` namespace (shipped in v0.19.0) |
| `pprint` | covered | `pprint` + `PrettyPrinter` (shipped in v0.20.0) |
| `reprlib` | out | POOP forbids `repr` |
| `enum` | covered | `enum` + `Enum` + `IntEnum` + `StrEnum` + `Flag` + `IntFlag` + `ReprEnum` (shipped in v0.35.0) |
| `graphlib` | covered | `graphlib` + `TopologicalSorter` (shipped in v0.28.0) |

### Numeric and Mathematical Modules

| Module | Status | Sketch |
|---|---|---|
| `numbers` | out | ABC hierarchy — POOP has its own type tree |
| `math` | covered | `Math` namespace (shipped in v0.6.0) |
| `cmath` | covered | `cmath` namespace (shipped in v0.53.0) |
| `decimal` | covered | `decimal` + `Decimal` + `Context` (shipped in v0.32.0) |
| `fractions` | covered | `fractions` + `Fraction` (shipped in v0.36.0) |
| `random` | covered | `Random` namespace (shipped in v0.7.0) |
| `statistics` | covered | `statistics` + `NormalDist` (shipped in v0.36.0) |

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
| `filecmp` | covered | `filecmp` + `Dircmp` (shipped in v0.38.0) |
| `tempfile` | covered | `tempfile` + `TemporaryFile` + `NamedTemporaryFile` + `SpooledTemporaryFile` + `TemporaryDirectory` (shipped in v0.38.0) |
| `glob` | covered | `glob` namespace + `GlobIter` (shipped in v0.17.0) |
| `fnmatch` | covered | `fnmatch` namespace (shipped in v0.18.0) |
| `linecache` | out | Internal traceback helper |
| `shutil` | covered | `shutil` namespace (shipped in v0.38.0) |

### Data Persistence

| Module | Status | Sketch |
|---|---|---|
| `pickle` | covered | `pickle` + `Pickler` + `Unpickler` (shipped in v0.39.0) |
| `copyreg` | out | Internal hook for `pickle` |
| `shelve` | out | Depends on `dbm` |
| `marshal` | out | CPython internal |
| `dbm` | out | Niche; prefer `sqlite3` |
| `sqlite3` | covered | `sqlite3` + `Connection` + `Cursor` + `Row` (shipped in v0.33.0) |

### Data Compression and Archiving

| Module | Status | Sketch |
|---|---|---|
| `zlib` | covered | `zlib` + `Compress` + `Decompress` (shipped in v0.40.0) |
| `gzip` | covered | `gzip` + `GzipFile` (shipped in v0.40.0) |
| `bz2` | covered | `bz2` + `BZ2File` + `BZ2Compressor` + `BZ2Decompressor` (shipped in v0.40.0) |
| `lzma` | covered | `lzma` + `LZMAFile` + `LZMACompressor` + `LZMADecompressor` (shipped in v0.40.0) |
| `zipfile` | covered | `zipfile` + `ZipFile` + `ZipInfo` (shipped in v0.40.0) |
| `tarfile` | covered | `tarfile` + `TarFile` + `TarInfo` (shipped in v0.40.0) |
| `compression` | covered | `compression` umbrella (shipped in v0.40.0) |

### File Formats

| Module | Status | Sketch |
|---|---|---|
| `csv` | covered | `csv` + `Reader` + `Writer` + `DictReader` + `DictWriter` + `Sniffer` (shipped in v0.43.0) |
| `configparser` | covered | `configparser` + `ConfigParser` + `RawConfigParser` (shipped in v0.43.0) |
| `tomllib` | covered | `tomllib` namespace (shipped in v0.26.0) |
| `netrc` | out | Niche legacy format |
| `plistlib` | out | macOS-specific niche |

### Cryptographic Services

| Module | Status | Sketch |
|---|---|---|
| `hashlib` | covered | `hashlib` + `Hash` (shipped in v0.30.0) |
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
| `threading` | covered | `threading` / `Thread` / `Lock` / `RLock` / `Event` / `Semaphore` / `Barrier` namespaces (v0.50.0) |
| `multiprocessing` | covered | `multiprocessing` / `Pool` / `MPQueue` namespaces (`Process` via the namespace) (v0.50.0) |
| `concurrent` | covered | `concurrent` / `ThreadPoolExecutor` / `ProcessPoolExecutor` / `CFFuture` namespaces (v0.50.0) |
| `subprocess` | covered | `subprocess` / `Popen` / `CompletedProcess` namespaces (v0.50.0) |
| `sched` | out | Niche scheduler |
| `queue` | covered | `queue` / `Queue` / `LifoQueue` / `PriorityQueue` / `SimpleQueue` namespaces (v0.50.0) |
| `contextvars` | out | Implementation detail |

### Networking and Interprocess Communication

| Module | Status | Sketch |
|---|---|---|
| `asyncio` | covered | `asyncio` / `Future` namespaces — `async def` methods allowed (v0.48.0, source allowance in v0.52.0) |
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
| `urllib` | covered | `urllib` + `Request` + `Response` + `ParseResult` + `SplitResult` (shipped in v0.42.0) |
| `http` | covered | `http` + `HTTPConnection` + `HTTPSConnection` + `HTTPResponse` + `SimpleCookie` + `Morsel` (shipped in v0.42.0) |
| `ftplib` | out | Legacy protocol |
| `poplib` | out | Legacy protocol |
| `imaplib` | out | Legacy protocol |
| `smtplib` | covered | `smtplib` + `SMTP` + `SMTP_SSL` + `LMTP` (shipped in v0.42.0) |
| `uuid` | covered | `uuid` + `UUID` (shipped in v0.24.0) |
| `socketserver` | out | Pairs with `socket` if ever |
| `ipaddress` | covered | `ipaddress` + `IPv4Address` + `IPv6Address` + `IPv4Network` + `IPv6Network` + `IPv4Interface` + `IPv6Interface` (shipped in v0.42.0) |

### Multimedia Services

| Module | Status | Sketch |
|---|---|---|
| `wave` | out | Niche audio format |
| `colorsys` | out | Tiny niche helper |

### Internationalization

| Module | Status | Sketch |
|---|---|---|
| `gettext` | out | Niche |
| `locale` | covered | `locale` namespace (shipped in v0.41.0) |

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
| `pwd` | covered | `pwd` + `Passwd` (shipped in v0.44.0) |
| `grp` | covered | `grp` + `Group` (shipped in v0.44.0) |
| `termios` / `tty` / `pty` | out | Low-level TTY |
| `fcntl` | out | Low-level file control |
| `resource` | covered | `resource` + `RUsage` (shipped in v0.44.0) |
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
