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

`string.Formatter` is deliberately out of scope — `Str.format(*args, **kwargs)` is CPython's `str.format` template method (overriding the inherited `Object.format(spec)`), which covers the common case.

`string` and `Template` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/string.py` — namespace-only, no AST rewrite.

### enum + Enum + IntEnum + StrEnum + Flag + IntFlag + ReprEnum — `poop/types/enum.py` + `poop/transformers/enum.py`

`enum` mirrors Python's `enum` module — typed enumeration classes (`class Color(Enum): RED = 1`). The standard CPython machinery is preserved (members, lookups, `@unique`, `auto()`, etc.) and POOP adds:

- `.name_str()` returning POOP `Str` — `.name` itself stays a Python `str` because CPython's enum machinery (and decorators like `@unique`) compare it for identity.
- `.value_object()` returning a wrapped POOP value (`Int`/`Str`/`Float`/`Boolean`) — `.value` returns whatever was assigned (raw Python primitives stay raw; POOP types pass through unchanged).
- `_missing_` is wired so `Color(Int(1))` resolves to `Color.RED` exactly like `Color(1)`.
- `Enum.iter()` returns a POOP `List` of members.
- Operator results are POOP-typed: `==`/`!=` answer a POOP `Boolean` (so `(state == State.IDLE).if_true(...)` works), `<`/`<=`/`>`/`>=` answer a `Boolean` for the int-based families, and `IntEnum`/`IntFlag` arithmetic (`LOW + HIGH`) answers a POOP `Int`. `__hash__` is preserved, so alias resolution and member-keyed dict lookup keep working; `IntFlag` bitwise `|`/`&`/`^`/`~` keep CPython's flag-combination semantics (they answer flag members).

| Operation | Returns | Notes |
|---|---|---|
| `class Color(Enum): RED = 1` | enum class | members are class-side singletons |
| `Color.RED.name` | Python `str` | matches Python's enum protocol |
| `Color.RED.name_str()` | `Str` | POOP-shaped name |
| `Color.RED.value` | whatever was assigned | raw Python primitive or POOP type |
| `Color.RED.value_object()` | `Int` / `Str` / `Float` / `Boolean` | wrapped POOP form |
| `Color(value)` / `Color(Int(value))` | enum member | POOP wrappers are unwrapped before lookup |
| `Enum("Color", names)` (functional API) | enum class | `names` may be a `List` of `Str`, a space/comma `Str`, or `List` of `(name, value)` `Tuple`s — unwrapped via a metaclass `__call__` before delegating |
| `Color.iter()` | `List` | materialized member list |
| `IntEnum` / `StrEnum` / `Flag` / `IntFlag` | enum classes | same POOP helpers, plus the data-type mixin from CPython |
| `ReprEnum` | enum class (re-exported) | requires a data-type mixin (`class Color(int, ReprEnum): ...`); `.name`/`.value` stay raw Python types in this path |
| `auto()` | sentinel | sequential value generation inside an enum body; on a plain `Enum` the value answers a POOP `Int` (like a literal member), while the primitive-mixed families (`IntEnum`/`IntFlag`/`StrEnum`) and `Flag` keep a raw value reachable via `.value_object()` |
| `enum.unique` / `verify` / `member` / `nonmember` (class attrs) | decorators | apply directly on enum classes |
| `enum.global_enum` / `pickle_by_enum_name` / `pickle_by_global_name` (class attrs) | decorators | module-level repr / pickling policy, re-exported from CPython |
| `enum.property` (class attr) | descriptor | enum-specific `@property` that coexists with member names |
| `enum.CONTINUOUS` / `NAMED_FLAGS` / `UNIQUE` (class attrs) | constants | for `@verify` |
| `enum.STRICT` / `CONFORM` / `EJECT` / `KEEP` (class attrs) | constants | `Flag` boundary policies (`boundary=` kwarg) |

`EnumType` metaclass access is out of scope (POOP forbids introspection).

`enum`, `Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `ReprEnum`, and `auto` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dict in `poop/transformers/enum.py` — namespace-only, no AST rewrite.

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

`HTTPStatus` (IntEnum) and `HTTPMethod` (StrEnum) are rebuilt over the POOP enum bases (from CPython's members) rather than re-exported, so members answer POOP messages — `==` returns a `Boolean` (so `(status == HTTPStatus.OK).if_true(...)` works for status dispatch), `.phrase`/`.description` return `Str`, and the `is_*` predicates return `Boolean`. The inherited `_missing_` unwraps POOP `Int`/`Str`, so `http.HTTPStatus(Int(200))` returns `HTTPStatus.OK`.

| Operation | Returns | Notes |
|---|---|---|
| `http.HTTPStatus` (class attr) | POOP `IntEnum` | `.OK` / `.NOT_FOUND` / … members; `.value` (raw int) / `.value_object()` (`Int`); `.phrase` / `.description` → `Str`; `.is_success` / `.is_client_error` / `.is_server_error` / `.is_redirection` / `.is_informational` → `Boolean` |
| `http.HTTPMethod` (class attr) | POOP `StrEnum` | `.GET` / `.POST` / `.PUT` / `.PATCH` / `.DELETE` / `.HEAD` / `.OPTIONS` / `.TRACE` / `.CONNECT`; `.description` → `Str` |
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
| `html.entities.name2codepoint()` | `Dict[Str, Int]` | |
| `html.entities.codepoint2name()` | `Dict[Int, Str]` | |
| `html.entities.entitydefs()` / `.html5()` | `Dict[Str, Str]` | |
| `HTMLParser(convert_charrefs=true)` | `HTMLParser` | SAX-style; subclass and override `handle_*` |
| `HTMLParser.feed(data)` / `.close()` / `.reset()` | `none` | |
| `HTMLParser.getpos()` | `Tuple(Int, Int)` | `(line, offset)` |
| `HTMLParser.get_starttag_text()` | `Str` / `none` | |
| `HTMLParser.handle_starttag(tag, attrs)` / `handle_startendtag` | `none` | override; `attrs` is `List(Tuple(Str, Str\|none))` |
| `HTMLParser.handle_endtag/data/comment/decl/pi/entityref/charref(...)` | `none` | override; args are `Str` |
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
| `Socket(family=AF_INET, type=SOCK_STREAM, proto=0)` | `Socket` | `With`-friendly (`With(lambda: Socket()).do(...)`) |
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
| `asyncio.gather(*coros, return_exceptions=false)` | awaitable | resolves to `List` of results; with `return_exceptions=true`, exceptions arrive wrapped as `Error` |
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
| `Formatter.default_time_format` / `default_msec_format` (class attrs) | `Str` | blessed as POOP `Str`; `formatTime` unwraps them, so assigning a POOP `Str` knob works |
| `Logger(name, level=none)` | `Logger` | direct construction mirrors CPython (standalone, level `NOTSET`) |
| `Filter(name=none)` | `Filter` | |
| Subclass `Filter` / `Handler` / `Formatter` and override `filter(record)` / `emit(record)` / `format(record)` | — | overrides routed through `block.bridge`; override receives the raw `_logging.LogRecord`, wrap it in `LogRecord(record)` for POOP-typed fields |
| `LogRecord(record)` exposes `.name` / `.msg` / `.args` / `.levelname` / `.levelno` / `.pathname` / `.filename` / `.module` / `.lineno` / `.funcName` / `.created` / `.thread` / `.threadName` / `.process` / `.processName` (properties) and `.getMessage()` | POOP types | wraps `_logging.LogRecord` for handler/formatter overrides |
| `LoggerAdapter(logger, extra=none)` plus `.debug` / `.info` / `.warning` / `.error` / `.critical` / `.log` / `.setLevel` | `LoggerAdapter` / `none` | passes `extra` through every log call |
| `BufferingFormatter(linefmt=none)` | `BufferingFormatter` | header/footer-aware batch formatter |
| `Logging.Filterer` / `PercentStyle` / `StrFormatStyle` / `StringTemplateStyle` (class attrs) | raw stdlib class refs | exposed for `isinstance` checks |
| `logging.exception(msg)` / `.disable(level=none)` / `.captureWarnings(flag)` / `.makeLogRecord(d)` | `none` / `LogRecord` | module-level helpers |
| `logging.getHandlerByName(name)` / `.getHandlerNames()` / `.getLevelNamesMapping()` | `Handler` or `none` / `List[Str]` / `Dict[Str, Int]` | introspection |
| `logging.getLogRecordFactory()` | `Block` | a POOP callable; calling it answers a POOP `LogRecord` |
| `logging.setLogRecordFactory(block)` | `none` | the block is handed POOP args and may answer a `LogRecord`; the stdlib side gets the raw record |
| `logging.getLoggerClass()` | `Logger` (POOP class) | instantiate it for a POOP `Logger`, not the raw `logging.Logger` |
| `logging.setLoggerClass(Logger)` | `none` | accepts the POOP `Logger` class, mapped to the raw class it manages |
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

### threading + Thread + Lock/RLock + Event + Semaphore/BoundedSemaphore + Condition + Barrier + Local, multiprocessing + Process + MPQueue + Pool, concurrent + ThreadPoolExecutor + ProcessPoolExecutor + CFFuture, subprocess + Popen + CompletedProcess, queue + Queue + LifoQueue + PriorityQueue + SimpleQueue — `poop/types/{threading,multiprocessing,concurrent,subprocess,queue}.py`

Five concurrent-execution namespaces shipped together. `threading` exposes `Thread` + the synchronisation primitives (`Lock`/`RLock`/`Event`/`Semaphore`/`BoundedSemaphore`/`Condition`/`Barrier`) — all primitives are `With`-friendly — plus `Local` (per-thread storage) and `threading.Timer`. `multiprocessing` mirrors the structure for cross-process execution: `Process` + `MPQueue` + `Pool` plus the module helpers. `concurrent.futures` exposes `ThreadPoolExecutor` + `ProcessPoolExecutor` + `CFFuture` (named to disambiguate from `asyncio.Future`). `subprocess` is the canonical shell-out API: high-level `run` (returning `CompletedProcess`), the backward-compat `call`/`check_call`/`check_output`/`getoutput`/`getstatusoutput`, and the full-lifecycle `Popen`. `queue` provides synchronised FIFO/LIFO/priority/simple queues.

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
| `BoundedSemaphore(value=1)` | primitive | `Semaphore` subclass; over-`release` raises `ValueError` |
| `Condition(lock=none)` | primitive | `With`-friendly; wraps a fresh `RLock` when `lock` omitted |
| `Condition.acquire(...)` / `.release()` / `.wait(timeout=none)` / `.wait_for(predicate, timeout=none)` / `.notify(n=1)` / `.notify_all()` | `Boolean` / `none` | `predicate` is a block |
| `Local()` | `Local` | per-thread storage; `at(name)` / `at_put(name, value)` / `includes(name)` |
| `threading.Timer(interval, function, args=none, kwargs=none)` | `Timer` | `start`/`cancel`/`join`/`is_alive`; namespace-only — a bare `Timer` would collide with `timeit.Timer` |
| `threading.current_thread()` / `.main_thread()` | `Thread` | |
| `threading.active_count()` / `.get_ident()` / `.get_native_id()` | `Int` | |
| `threading.stack_size(size=none)` | `Int` | |
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
| `Popen` as context manager (`with`) | `Popen` | closes the `PIPE` streams and waits on exit, releasing the pipe fds |
| `subprocess.PIPE` / `STDOUT` / `DEVNULL` (class attrs) | `Int` | |
| `subprocess.SubprocessError` / `CalledProcessError` / `TimeoutExpired` (class attrs) | exception class | |
| `Queue(maxsize=none)` / `LifoQueue(maxsize=none)` / `PriorityQueue(maxsize=none)` / `SimpleQueue()` | queue | |
| `Queue.put(item, block=true, timeout=none)` / `.get(...)` / `.put_nowait` / `.get_nowait` / `.qsize` / `.empty` / `.full` | typed | |
| `Queue.task_done()` / `.join()` | `none` | LifoQueue/PriorityQueue also expose these |
| `queue.Empty` / `Full` (class attrs) | exception class | |

`threading`/`Thread`/`Lock`/`RLock`/`Event`/`Semaphore`/`BoundedSemaphore`/`Condition`/`Local`/`Barrier`/`multiprocessing`/`Pool`/`MPQueue`/`concurrent`/`ThreadPoolExecutor`/`ProcessPoolExecutor`/`CFFuture`/`subprocess`/`Popen`/`CompletedProcess`/`queue`/`Queue`/`LifoQueue`/`PriorityQueue`/`SimpleQueue` are exposed in `DEFAULT_NAMESPACE` via the `NAMESPACE` dicts in `poop/transformers/{threading,multiprocessing,concurrent,subprocess,queue}.py` — namespace-only, no AST rewrite. `multiprocessing.Process` is **only reachable via `multiprocessing.Process`** (not bound as a top-level name) — that matches Python's idiomatic usage and avoids ambiguity with future `Process`-named types. POOP's `Block` (lambda-wrapping) does not pickle across the `multiprocessing` boundary on `forkserver` start methods — module-level Python functions must be used as `target=...` for `Process` / `Pool` workers.

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
