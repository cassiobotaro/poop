# Proposals

## Expose `os` as POOP messages

Python's `os` is huge — process management, environment, file
descriptors, file system ops not covered by `pathlib`. POOP splits
it into focused namespaces rather than one monolithic mirror.

**Proposal — four POOP namespaces (`os`, `system`, `process`,
`env`) drawn from `os`:**

1. **`os` (lowercase)** binds the four sub-namespaces and a small
   set of file-system numerics that `Path` doesn't cover:
   `os.urandom(n) -> Bytes`, `os.cpu_count() -> Int`,
   `os.process_cpu_count() -> Int`, `os.getloadavg() -> Tuple[Float]`,
   plus path-mode constants (`F_OK`, `R_OK`, `W_OK`, `X_OK`,
   `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_APPEND`, `O_CREAT`, …)
   when those are needed for low-level FD ops.
2. **`system`** namespace for process-level state:
   `system.exit(code=0)`, `system.argv -> Tuple[Str]` (replaces
   `sys.argv`), `system.executable -> Path`, `system.platform -> Str`.
3. **`process`** namespace for current-process operations:
   `process.pid -> Int`, `process.ppid -> Int`,
   `process.uid` / `process.gid` / `process.euid` / `process.egid` /
   `process.umask(mask) -> Int`, `process.chdir(path)`,
   `process.getcwd() -> Path`, `process.kill(pid, signal)`.
4. **`env`** namespace for environment variables:
   `env.get(key, default=None) -> Str | NoneClass`,
   `env.set(key, value) -> NoneClass`, `env.unset(key)`,
   `env.has(key) -> Boolean`, `env.keys() -> Set[Str]`,
   iteration via `.do(block)`, `Dict`-like API.

**Type discipline:** `Path` for filesystem, `Str` for env values,
`Int` for IDs/file-descriptors.

**Out of scope (for v1):**

- The `os.path` family — fully covered by `Path`.
- `os.spawn*` / `os.exec*` / `os.fork()` — `subprocess` proposal
  covers process creation; raw fork/exec is unsafe by default.
- The low-level FD API (`os.open`/`read`/`write`/`close`) — use
  `Path.read_bytes`/`write_bytes` or future streaming I/O instead.

## Expose `io` as POOP messages

Python's `io` covers in-memory and stream I/O. Most file I/O lives
in `Path`; this proposal exposes only the in-memory and streaming
extras.

**Proposal — `io` (lowercase module) + class set:**

1. **In-memory:**
   `io.StringIO(initial_value='', newline='\n')` — text buffer,
   `io.BytesIO(initial_bytes=b'')` — binary buffer.
   Both expose `.read`, `.write`, `.getvalue`, `.seek`, `.tell`,
   `.truncate`, `.close`, `With` context-manager friendly.
2. **Stream bases** (for advanced users implementing custom
   streams): `io.IOBase`, `io.RawIOBase`, `io.BufferedIOBase`,
   `io.TextIOBase`.
3. **Constants:** `io.SEEK_SET`, `io.SEEK_CUR`, `io.SEEK_END`,
   `io.DEFAULT_BUFFER_SIZE`.
4. **Errors:** `io.UnsupportedOperation`, `io.BlockingIOError`.

**Type discipline:** `Str` for `StringIO`, `Bytes` for `BytesIO`,
`Int` for sizes/positions.

**Out of scope (for v1):**

- `io.open` — `Path.read_text` / `write_text` is the POOP idiom.
- `io.IncrementalNewlineDecoder` — niche.

## Expose `time` as POOP messages

Python's `time` is the wall-clock/monotonic clock API. Pairs with
`datetime` but lower-level.

**Proposal — `time` (lowercase module) namespace:**

1. **Clocks:**
   `time.time() -> Float` (wall-clock seconds since epoch),
   `time.time_ns() -> Int`,
   `time.monotonic() -> Float`,
   `time.monotonic_ns() -> Int`,
   `time.perf_counter() -> Float`,
   `time.perf_counter_ns() -> Int`,
   `time.process_time() -> Float`,
   `time.process_time_ns() -> Int`,
   `time.thread_time() -> Float`,
   `time.thread_time_ns() -> Int`.
2. **Sleep:** `time.sleep(seconds) -> NoneClass`.
3. **Formatting / parsing:**
   `time.strftime(format, time_tuple=None) -> Str`,
   `time.strptime(string, format) -> StructTime`,
   `time.gmtime(secs=None) -> StructTime`,
   `time.localtime(secs=None) -> StructTime`,
   `time.mktime(struct_time) -> Float`,
   `time.asctime(struct_time=None) -> Str`,
   `time.ctime(secs=None) -> Str`.
4. **`StructTime` class** wrapping `time.struct_time`: nine-attr
   record (`tm_year`, `tm_mon`, `tm_mday`, `tm_hour`, `tm_min`,
   `tm_sec`, `tm_wday`, `tm_yday`, `tm_isdst`, `tm_zone`,
   `tm_gmtoff`).
5. **Timezone info:** `time.tzname`, `time.timezone`,
   `time.altzone`, `time.daylight`, `time.tzset()`.

**Type discipline:** `Float`/`Int` for clocks/durations, `Str` for
formatted output, `StructTime` for structured time.

## Expose `logging` as POOP messages

Python's `logging` is the canonical logging framework: loggers,
handlers, formatters, filters, levels.

**Proposal — `logging` (lowercase module) + class set:**

1. **Module-level convenience:**
   `logging.debug(msg, *args, **kwargs)`,
   `logging.info(...)`, `logging.warning(...)`,
   `logging.error(...)`, `logging.critical(...)`,
   `logging.exception(...)`, `logging.log(level, msg, *args, **kwargs)`,
   `logging.getLogger(name=None) -> Logger`,
   `logging.basicConfig(**kwargs) -> NoneClass`.
2. **`Logger` class** — `.debug/info/warning/error/critical/log`,
   `.setLevel(level)`, `.isEnabledFor(level) -> Boolean`,
   `.addHandler(h)`, `.removeHandler(h)`, `.handlers -> List[Handler]`,
   `.propagate -> Boolean`, `.getEffectiveLevel() -> Int`.
3. **`Handler` class + subclasses:** `StreamHandler`, `FileHandler`,
   `NullHandler`. Methods `.setLevel`, `.setFormatter(f)`,
   `.addFilter`, `.removeFilter`, `.emit(record)`.
4. **`Formatter` class:** `Formatter(fmt=None, datefmt=None, style='%', validate=True, *, defaults=None)`,
   `.format(record) -> Str`.
5. **`LogRecord` class** — emitted message + context (name, level,
   pathname, lineno, msg, args, exc_info, …).
6. **Filter** class + `Logger.addFilter`.
7. **Level constants:** `CRITICAL=50`, `ERROR=40`, `WARNING=30`,
   `INFO=20`, `DEBUG=10`, `NOTSET=0`. Plus
   `logging.getLevelName(level) -> Str`,
   `logging.addLevelName(level, name)`.

**Type discipline:** all POOP types — `Str` for messages/levels,
`Int` for level integers, `Dict` for `extra`/`defaults`.

**Out of scope (for v1):**

- `logging.config` (file + dict-based configuration) — niche, fold
  into a follow-up.
- `logging.handlers` (rotating, SMTP, syslog, …) — separate
  proposal.

## Expose `platform` as POOP messages

Python's `platform` returns information about the runtime
environment: OS, architecture, Python build.

**Proposal — `platform` (lowercase module) namespace, all functions
return POOP `Str` or POOP `Tuple`:**

1. **OS info:** `platform.system()`, `platform.release()`,
   `platform.version()`, `platform.machine()`, `platform.processor()`,
   `platform.platform(aliased=False, terse=False)`,
   `platform.node()`, `platform.uname() -> Uname`.
2. **Architecture:** `platform.architecture(executable=sys.executable, bits='', linkage='') -> Tuple[Str, Str]`.
3. **Python build:** `platform.python_version()`,
   `platform.python_version_tuple() -> Tuple[Str]`,
   `platform.python_branch()`, `platform.python_build() -> Tuple[Str, Str]`,
   `platform.python_compiler()`, `platform.python_implementation()`,
   `platform.python_revision()`.
4. **Per-OS specifics:** `platform.mac_ver()`, `platform.win32_ver()`,
   `platform.libc_ver()`.
5. **`Uname` class** — named record with `.system`, `.node`,
   `.release`, `.version`, `.machine`, `.processor`.

**Type discipline:** `Str` for textual fields, `Tuple` for
multi-value, named record for `Uname`.

**Out of scope (for v1):** the deprecated `dist()` / `linux_distribution()`.

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

## Expose `asyncio` as POOP messages

Python's `asyncio` is the largest stdlib module: event loop,
coroutines, futures, streams, queues, subprocess, locks. POOP needs
async to interact with modern Python ecosystems (web servers, DBs).
This proposal scopes a minimal-but-useful v1.

**Proposal — `asyncio` (lowercase module) + class set:**

1. **High-level entry points:**
   `asyncio.run(coro, *, debug=None, loop_factory=None) -> Object`,
   `asyncio.gather(*aws, return_exceptions=False) -> Future`,
   `asyncio.wait(aws, *, timeout=None, return_when=ALL_COMPLETED) -> Tuple[Set[Task], Set[Task]]`,
   `asyncio.wait_for(aw, timeout) -> Object`,
   `asyncio.shield(aw) -> Future`,
   `asyncio.sleep(delay, result=None) -> Object`,
   `asyncio.timeout(delay) -> Timeout`,
   `asyncio.timeout_at(when) -> Timeout`.
2. **Task/Future:** `asyncio.create_task(coro, *, name=None, context=None) -> Task`,
   `asyncio.current_task() -> Task | NoneClass`,
   `asyncio.all_tasks(loop=None) -> Set[Task]`,
   `Task` and `Future` POOP classes.
3. **Event loop:** `asyncio.get_event_loop() -> AbstractEventLoop`,
   `asyncio.new_event_loop()`, `asyncio.set_event_loop(loop)`,
   `asyncio.get_running_loop()`. (Most users don't need this with
   `asyncio.run`.)
4. **Sync primitives (async-aware):** `asyncio.Lock`, `Event`,
   `Condition`, `Semaphore`, `BoundedSemaphore`, `Barrier`.
5. **`asyncio.Queue`** (FIFO), `LifoQueue`, `PriorityQueue`.
6. **`asyncio.TaskGroup`** (3.11+) for structured concurrency.
7. **Streams:** `asyncio.StreamReader`, `StreamWriter`,
   `asyncio.open_connection`, `asyncio.start_server`.
8. **Errors:** `CancelledError`, `InvalidStateError`,
   `SendfileNotAvailableError`, `IncompleteReadError`,
   `LimitOverrunError`, `TimeoutError` (3.11+ unified).

**Type discipline:** coroutines as POOP `Block`-equivalent
callables; results in POOP types end-to-end.

**Out of scope (for v1):**

- Transport/Protocol low-level API — use Streams instead.
- `asyncio.subprocess`, `asyncio.unix_events`, `asyncio.windows_events`
  — pair with future `subprocess` async story.

## Expose `socket` as POOP messages

Python's `socket` is the low-level network API: TCP, UDP, Unix
sockets, name resolution. Big surface; this proposal scopes v1 to
the common shape.

**Proposal — `socket` (lowercase module) + `Socket` class:**

1. **`Socket` class** wrapping `socket.socket`:
   `Socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)`,
   `.bind(address)`, `.listen(backlog=0)`,
   `.accept() -> Tuple[Socket, Address]`,
   `.connect(address)`, `.connect_ex(address) -> Int`,
   `.send(bytes, flags=0) -> Int`,
   `.sendall(bytes, flags=0) -> NoneClass`,
   `.sendto(bytes, address)`, `.sendmsg(...)`,
   `.recv(bufsize, flags=0) -> Bytes`,
   `.recvfrom(bufsize) -> Tuple[Bytes, Address]`,
   `.recv_into(buffer, nbytes=0, flags=0)`, `.recvmsg(...)`,
   `.close()`, `.shutdown(how)`,
   `.setsockopt`/`.getsockopt`, `.settimeout`/`.gettimeout`,
   `.setblocking(flag)`,
   `.fileno() -> Int`,
   `.getsockname()`, `.getpeername()`,
   `.makefile(mode='r', buffering=None, *, encoding=None, errors=None, newline=None) -> File`.
2. **Module-level helpers:**
   `socket.create_connection(address, timeout=None, source_address=None, *, all_errors=False) -> Socket`,
   `socket.create_server(address, *, family=AF_INET, backlog=None, reuse_port=False, dualstack_ipv6=False) -> Socket`,
   `socket.has_dualstack_ipv6() -> Boolean`,
   `socket.gethostname() -> Str`,
   `socket.gethostbyname(host) -> Str`,
   `socket.gethostbyname_ex(host) -> Tuple[Str, List, List]`,
   `socket.gethostbyaddr(addr) -> Tuple`,
   `socket.getaddrinfo(host, port, family=0, type=0, proto=0, flags=0) -> List[Tuple]`,
   `socket.getfqdn(name='') -> Str`,
   `socket.getservbyname(servicename, protocolname=None) -> Int`,
   `socket.getservbyport(port, protocolname=None) -> Str`,
   `socket.htons`/`htonl`/`ntohs`/`ntohl`,
   `socket.inet_aton(ip_string) -> Bytes`,
   `socket.inet_ntoa(packed_ip) -> Str`,
   `socket.inet_pton(family, ip_string) -> Bytes`,
   `socket.inet_ntop(family, packed_ip) -> Str`.
3. **Constants:** address families (`AF_INET`, `AF_INET6`,
   `AF_UNIX`, `AF_BLUETOOTH`, …), socket types (`SOCK_STREAM`,
   `SOCK_DGRAM`, `SOCK_RAW`, …), socket options (`SO_REUSEADDR`,
   `SO_KEEPALIVE`, …).
4. **Errors:** `socket.error` (alias of `OSError`),
   `socket.herror`, `socket.gaierror`, `socket.timeout` (alias of
   `TimeoutError`).

**Type discipline:** `Bytes` for buffers, `Str` for hostnames/IPs,
`Int` for ports/sizes/fileno, `Tuple` for addresses.

## Expose `ssl` as POOP messages

Python's `ssl` wraps a socket with TLS/SSL. Pairs with `socket`.

**Proposal — `ssl` (lowercase module) + class set:**

1. **`SSLContext` class:**
   `ssl.create_default_context(purpose=Purpose.SERVER_AUTH, *, cafile=None, capath=None, cadata=None) -> SSLContext`,
   `ssl.SSLContext(protocol=PROTOCOL_TLS_CLIENT)`,
   `.load_cert_chain(certfile, keyfile=None, password=None)`,
   `.load_verify_locations(cafile=None, capath=None, cadata=None)`,
   `.load_default_certs(purpose=Purpose.SERVER_AUTH)`,
   `.wrap_socket(sock, ...)`, `.wrap_bio(...)`,
   `.set_ciphers(ciphers)`, `.get_ciphers() -> List[Dict]`,
   `.minimum_version`, `.maximum_version`, `.verify_mode`,
   `.check_hostname`.
2. **`SSLSocket` class** — `socket.Socket` plus SSL-specific:
   `.do_handshake()`, `.getpeercert(binary_form=False) -> Dict`,
   `.cipher() -> Tuple[Str, Str, Int]`,
   `.compression() -> Str | NoneClass`,
   `.selected_alpn_protocol() -> Str | NoneClass`,
   `.version() -> Str | NoneClass`,
   `.session -> SSLSession`,
   `.unwrap() -> Socket`.
3. **Constants:** `PROTOCOL_TLS_CLIENT`, `PROTOCOL_TLS_SERVER`,
   `CERT_NONE`, `CERT_OPTIONAL`, `CERT_REQUIRED`,
   `Purpose.SERVER_AUTH`, `Purpose.CLIENT_AUTH`,
   `TLSVersion.MINIMUM_SUPPORTED`/`TLSv1_2`/`TLSv1_3`/etc.
4. **Errors:** `SSLError`, `SSLZeroReturnError`,
   `SSLWantReadError`, `SSLWantWriteError`, `SSLSyscallError`,
   `SSLEOFError`, `SSLCertVerificationError`.

**Type discipline:** all POOP types.

**Out of scope (for v1):** `ssl.RAND_*` (PRNG seeding — POOP uses
`secrets`), the deprecated PEM password callback machinery.

## Expose `signal` as POOP messages

Python's `signal` installs handlers for OS signals and inspects
signal state.

**Proposal — `signal` (lowercase module) namespace:**

1. **Handler registration:**
   `signal.signal(signalnum, handler) -> previous_handler`,
   `signal.getsignal(signalnum) -> handler`,
   `signal.set_wakeup_fd(fd, *, warn_on_full_buffer=True) -> Int`.
2. **Querying:** `signal.pthread_kill(thread_id, signum)`,
   `signal.pthread_sigmask(how, mask) -> Set[Int]`,
   `signal.sigpending() -> Set[Int]`,
   `signal.sigwait(sigset) -> Int`, `signal.sigwaitinfo(sigset)`,
   `signal.sigtimedwait(sigset, timeout)`.
3. **Timers (Unix):** `signal.setitimer(which, seconds, interval=0)`,
   `signal.getitimer(which)`.
4. **Constants:** all `SIG*` signal numbers Python ships
   (`SIGABRT`, `SIGINT`, `SIGTERM`, `SIGKILL`, `SIGCHLD`,
   `SIGUSR1`, `SIGUSR2`, …) plus default-handler sentinels
   (`SIG_DFL`, `SIG_IGN`) and itimer kinds (`ITIMER_REAL`,
   `ITIMER_VIRTUAL`, `ITIMER_PROF`).
5. **Helpers:** `signal.strsignal(signalnum) -> Str | NoneClass`,
   `signal.Signals` IntEnum + `signal.Handlers` IntEnum +
   `signal.Sigmasks` IntEnum.

**Type discipline:** `Int` for signal numbers; callable POOP
`Block` for handlers; `Set[Int]` for sig sets.

**Out of scope (for v1):** `signal.SIGRTMIN`/`SIGRTMAX` real-time
signal range — niche.

## Expose `email` as POOP messages

Python's `email` package handles MIME messages: parse, build,
manipulate, generate. Sub-packages: `email.message`, `email.parser`,
`email.generator`, `email.policy`, `email.utils`, `email.headerregistry`,
`email.contentmanager`, `email.iterators`.

**Proposal — `email` (lowercase package) + class set:**

1. **`EmailMessage` class** (modern, 3.4+):
   `EmailMessage(policy=default)`, `.set_content(content, subtype='plain', ...)`,
   `.add_alternative(...)`, `.add_related(...)`, `.add_attachment(...)`,
   `.get_body(preferencelist=('related', 'html', 'plain'))`,
   `.get_content()`, `.iter_attachments()`, `.iter_parts()`,
   header manipulation as dict-like, `.is_multipart() -> Boolean`.
2. **Parser:** `email.message_from_string(s, _class=EmailMessage, *, policy=default) -> EmailMessage`,
   `email.message_from_bytes(b, ...)`, `message_from_file(fp, ...)`,
   `message_from_binary_file(fp, ...)`. Plus `BytesParser`/`Parser`
   classes for streaming.
3. **Generator:** `email.generator.Generator`, `BytesGenerator` for
   serialising back to text/bytes.
4. **Policy:** `email.policy.default`, `email.policy.SMTP`,
   `email.policy.SMTPUTF8`, `email.policy.HTTP`,
   `email.policy.strict`, `email.policy.compat32`.
5. **Utils:** `email.utils.parseaddr(address) -> Tuple[Str, Str]`,
   `email.utils.formataddr(pair, charset='utf-8') -> Str`,
   `email.utils.getaddresses(fieldvalues) -> List[Tuple]`,
   `email.utils.parsedate(date) -> Tuple | NoneClass`,
   `email.utils.parsedate_tz(date)`, `email.utils.mktime_tz(tuple)`,
   `email.utils.formatdate(timeval=None, localtime=False, usegmt=False) -> Str`,
   `email.utils.format_datetime(dt, usegmt=False) -> Str`,
   `email.utils.localtime(dt=None) -> DateTime`,
   `email.utils.make_msgid(idstring=None, domain=None) -> Str`.

**Type discipline:** `Str`/`Bytes` for content, `DateTime` for
date values (depends on `datetime` proposal), `EmailMessage` as
the POOP record.

**Out of scope (for v1):**

- `email.errors` deep hierarchy — expose only the parent
  `MessageError`/`MessageParseError`.
- Compat32-only convenience constructors (legacy).

## Expose `html` as POOP messages

Python's `html` is small: escape/unescape entities, plus
`html.parser.HTMLParser` for SAX-style parsing and
`html.entities` for the name⇄codepoint maps.

**Proposal — `html` (lowercase package) + `HTMLParser` class:**

1. **Escape/unescape:** `html.escape(s, quote=True) -> Str`,
   `html.unescape(s) -> Str`.
2. **`html.parser.HTMLParser` class** (SAX-style):
   `HTMLParser(*, convert_charrefs=True)`,
   `.feed(data)`, `.close()`, `.reset()`, `.getpos() -> Tuple[Int, Int]`,
   `.get_starttag_text() -> Str | NoneClass`.
   Override hooks: `.handle_starttag`, `.handle_endtag`,
   `.handle_startendtag`, `.handle_data`, `.handle_entityref`,
   `.handle_charref`, `.handle_comment`, `.handle_decl`,
   `.handle_pi`, `.unknown_decl`.
3. **`html.entities` namespace:** `name2codepoint -> Dict[Str, Int]`,
   `codepoint2name -> Dict[Int, Str]`, `html5 -> Dict[Str, Str]`,
   `entitydefs -> Dict[Str, Str]`.

**Type discipline:** `Str` for HTML strings, `Int` for codepoints,
`Tuple[Int, Int]` for parser position.

## Expose `xml` as POOP messages

Python's `xml` is a package covering parse/build for XML: DOM (`xml.dom`,
`xml.dom.minidom`), SAX (`xml.sax`), and ElementTree (`xml.etree.ElementTree`,
the preferred API). Scope v1 to ElementTree + the safer `defusedxml`
posture for the others.

**Proposal — `xml` (lowercase package), focused on ElementTree:**

1. **`xml.etree.ElementTree` (`ET`) namespace:**
   - `ET.parse(source, parser=None) -> ElementTree`,
     `ET.fromstring(text, parser=None) -> Element`,
     `ET.fromstringlist(sequence, parser=None) -> Element`,
     `ET.tostring(element, encoding=None, method='xml', short_empty_elements=True, xml_declaration=None, default_namespace=None) -> Bytes | Str`,
     `ET.tostringlist(...)`,
     `ET.XML(text, parser=None)` (alias of `fromstring`),
     `ET.XMLID(text, parser=None) -> Tuple[Element, Dict]`,
     `ET.iterparse(source, events=('end',), parser=None) -> Map`,
     `ET.canonicalize(...)`.
   - `ET.indent(tree, space='  ', level=0) -> NoneClass`.
2. **`Element` class** — node with tag, attributes, children,
   text/tail. Methods `.append`, `.extend`, `.insert`, `.remove`,
   `.find`, `.findall`, `.findtext`, `.iter`, `.iterfind`,
   `.iterancestors`, `.iterdescendants`, `.itertext`,
   `.keys` / `.items` / `.attrib` / `.get`, `.set`, `.clear`,
   `.getchildren` (deprecated), `.makeelement`.
3. **`ElementTree` class** — document-level: `.getroot()`,
   `.parse(source, parser=None)`, `.write(file, ...)`,
   `.write_c14n(...)`, `.iter()`, `.iterfind()`, `.find()`,
   `.findall()`, `.findtext()`.
4. **Builder/parser classes:** `TreeBuilder`, `XMLParser`,
   `XMLPullParser`.
5. **Errors:** `ParseError`.
6. **`xml.dom` minimal aliases:** expose only `Node` constants
   (`ELEMENT_NODE`, `ATTRIBUTE_NODE`, …) — the full minidom API
   is out of scope.

**Type discipline:** `Element` is a POOP class. Attributes as POOP
`Dict[Str, Str]`. Tags/text as `Str`.

**Out of scope (for v1):**

- `xml.sax`, `xml.dom.minidom`, `xml.dom.pulldom`, `xml.dom.expatbuilder` —
  the SAX and full-DOM APIs are largely superseded by ElementTree.
- `xml.dom.NodeFilter` and other DOM-specific helpers.
- Loading external DTDs / general entity expansion — POOP defaults
  to the safe parser configuration (no entity expansion) to avoid
  XXE attacks. Document explicitly.

## Expose `unittest` as POOP messages

Python's `unittest` is the canonical test framework (xUnit style).
POOP currently has no testing API; tests live in pytest at the
Python layer. Exposing `unittest` lets users write tests in POOP
source.

**Proposal — `unittest` (lowercase module) + class set:**

1. **`TestCase` class** — base for test methods. Methods to
   override: `.setUp()`, `.tearDown()`, `.setUpClass()`,
   `.tearDownClass()`, `.setUpModule()`/`.tearDownModule()`.
   Per-test assertions: `.assertEqual`, `.assertNotEqual`,
   `.assertTrue`, `.assertFalse`, `.assertIs`, `.assertIsNot`,
   `.assertIsNone`, `.assertIsNotNone`, `.assertIn`,
   `.assertNotIn`, `.assertIsInstance`, `.assertNotIsInstance`,
   `.assertRaises`, `.assertRaisesRegex`, `.assertWarns`,
   `.assertWarnsRegex`, `.assertLogs`, `.assertNoLogs`,
   `.assertAlmostEqual`, `.assertNotAlmostEqual`, `.assertGreater`,
   `.assertGreaterEqual`, `.assertLess`, `.assertLessEqual`,
   `.assertRegex`, `.assertNotRegex`, `.assertCountEqual`,
   `.assertMultiLineEqual`, `.assertSequenceEqual`,
   `.assertListEqual`, `.assertTupleEqual`, `.assertSetEqual`,
   `.assertDictEqual`, `.fail`, `.skipTest`. Plus the
   `.subTest(msg=None, **params)` context manager and
   `.addCleanup(function, *args, **kwargs)`.
2. **Decorators:** `@unittest.skip(reason)`,
   `@unittest.skipIf(condition, reason)`,
   `@unittest.skipUnless(condition, reason)`,
   `@unittest.expectedFailure`,
   `@unittest.skipIfCondition`.
3. **`TestSuite`/`TestLoader`/`TestRunner`/`TestResult`** classes
   for orchestration.
4. **Main:** `unittest.main(...)` (module-level test runner).
5. **Mock support:** `unittest.mock` sub-namespace with `Mock`,
   `MagicMock`, `AsyncMock`, `PropertyMock`, `patch`,
   `patch.object`, `patch.dict`, `patch.multiple`, `sentinel`,
   `DEFAULT`, `call`, `create_autospec`.
6. **Errors:** `SkipTest`.

**Type discipline:** all POOP types; assertions raise POOP
`AssertionError` on failure (`obj.assert_(msg)` already exists).

**Out of scope (for v1):**

- `IsolatedAsyncioTestCase` — pairs with the `asyncio` proposal.
- The `unittest.test_runner` machinery — niche extension point.

## Expose `profile` / `cProfile` / `pstats` as POOP messages

Python's `profile` (pure-Python) and `cProfile` (C-accelerated)
share the same API for deterministic profiling. `pstats` formats
the results.

**Proposal — `cProfile` (lowercase module, the C variant is
default) + `pstats` (lowercase module):**

1. **`cProfile` namespace:**
   `cProfile.run(command, filename=None, sort=-1) -> NoneClass`,
   `cProfile.runctx(command, globals, locals, filename=None, sort=-1)`,
   `cProfile.Profile(timer=None, timeunit=0.0, subcalls=True, builtins=True)` class
   with `.enable()`, `.disable()`, `.create_stats()`, `.print_stats(sort=-1)`,
   `.dump_stats(file)`, `.run(cmd)`, `.runctx(cmd, globals, locals)`,
   `.runcall(func, /, *args, **kwargs)`,
   context-manager friendly via `With`.
2. **`pstats` namespace:** `pstats.Stats(*filenames_or_profiles, stream=None)` class
   with `.add(*filenames_or_profiles)`, `.dump_stats(filename)`,
   `.sort_stats(*keys) -> Stats`, `.reverse_order()`,
   `.print_stats(*restrictions)`, `.print_callers(*restrictions)`,
   `.print_callees(*restrictions)`, `.strip_dirs()`, `.calc_callees()`.
3. **`pstats.SortKey`** enum: `CALLS`, `CUMULATIVE`, `FILENAME`,
   `LINE`, `NAME`, `NFL`, `PCALLS`, `STDNAME`, `TIME`.

**Type discipline:** `Path` for filenames, `Str` for sort keys
(via the `SortKey` enum), POOP `Profile`/`Stats` classes for the
state objects.

**Out of scope (for v1):** the pure-Python `profile` flavour
— exposing only `cProfile` is the modern convention; `profile.Profile`
becomes an alias.

## Expose `timeit` as POOP messages

Python's `timeit` measures small code snippet performance.

**Proposal — `timeit` (lowercase module) + `Timer` class:**

1. **Module-level shortcuts:**
   `timeit.timeit(stmt='pass', setup='pass', timer=time.perf_counter, number=1000000, globals=None) -> Float`,
   `timeit.repeat(stmt='pass', setup='pass', timer=time.perf_counter, repeat=5, number=1000000, globals=None) -> List[Float]`,
   `timeit.default_timer -> Block` (currently `time.perf_counter`).
2. **`Timer` class:**
   `Timer(stmt='pass', setup='pass', timer=time.perf_counter, globals=None)`,
   `.timeit(number=1000000) -> Float`,
   `.repeat(repeat=5, number=1000000) -> List[Float]`,
   `.autorange(callback=None) -> Tuple[Int, Float]`,
   `.print_exc(file=None)`.

**Type discipline:** `Float` for durations, `Int` for counts,
`List[Float]` for repeat results, `Str` or callable for code
snippets.

## Expose `sys` as POOP messages

Python's `sys` is the runtime introspection grab-bag. POOP forbids
broad introspection but still needs the runtime-state pieces:
argv, stdin/stdout/stderr, exit, executable path. Like `os`, POOP
splits the module into focused namespaces.

**Proposal — four POOP namespaces drawn from `sys`:**

1. **`sys`** (lowercase) binds the four sub-namespaces and the
   misc helpers that don't fit elsewhere:
   `sys.exit(code=0)`, `sys.executable -> Path`,
   `sys.platform -> Str`, `sys.version -> Str`,
   `sys.version_info -> Tuple`, `sys.implementation`,
   `sys.maxsize -> Int`, `sys.byteorder -> Str`,
   `sys.flags`, `sys.float_info`, `sys.int_info`,
   `sys.hash_info`, `sys.thread_info`,
   `sys.modules -> Dict[Str, module]` (read-only view),
   `sys.path -> List[Str]`,
   `sys.getrecursionlimit() -> Int`,
   `sys.setrecursionlimit(limit)`.
2. **`args`** (lowercase) — read-only view of `sys.argv`:
   `args.list -> List[Str]`, `args.script -> Str`,
   `args.rest -> List[Str]`, iteration via `.do`.
3. **`stdout` / `stderr`** namespaces (POOP-flavoured) —
   `stdout.write(s)`, `stdout.writeln(s)`, `stdout.flush()`,
   `stdout.isatty() -> Boolean`. Same shape for `stderr`.
4. **`stdin`** namespace — `stdin.read() -> Str`,
   `stdin.readline() -> Str`, `stdin.readlines() -> List[Str]`,
   `stdin.isatty()`, iteration over lines.

**Type discipline:** `Str`/`Int`/`Path` end-to-end. `sys.modules`
keys are `Str`, values are opaque module objects (Python-only).

**Out of scope (for v1):**

- `sys.setprofile`/`settrace`/`monitoring` — introspection ban.
- `sys._getframe`, `sys._current_frames` — frame introspection
  forbidden.
- `sys.audit`/`sys.addaudithook` — niche.
- `sys.set_int_max_str_digits` etc. — runtime tuning niche.

## Expose `atexit` as POOP messages

Python's `atexit` registers callables to run at interpreter shutdown.
Tiny module.

**Proposal — `atexit` (lowercase module) namespace:**

1. **`atexit.register(func, *args, **kwargs) -> Block`** — also
   usable as decorator; returns the registered callable.
2. **`atexit.unregister(func) -> NoneClass`**.
3. **`atexit._run_exitfuncs() -> NoneClass`** — manual trigger
   (testing only).
4. **`atexit._clear() -> NoneClass`** — drop all registrations
   (testing only).

**Type discipline:** callable POOP `Block` in/out.

## Expose `gc` as POOP messages

Python's `gc` is the garbage collector control + introspection.
POOP forbids broad introspection, but the control surface is fine
to expose.

**Proposal — `gc` (lowercase module) namespace, control surface
only:**

1. **Toggle:** `gc.enable()`, `gc.disable()`,
   `gc.isenabled() -> Boolean`.
2. **Force a cycle:** `gc.collect(generation=2) -> Int` (returns
   unreachable count).
3. **Thresholds:** `gc.get_threshold() -> Tuple[Int, Int, Int]`,
   `gc.set_threshold(threshold0, threshold1=None, threshold2=None)`.
4. **Stats:** `gc.get_count() -> Tuple[Int, Int, Int]`,
   `gc.get_stats() -> List[Dict]`.
5. **Debug flags:** `gc.get_debug() -> Int`, `gc.set_debug(flags)`,
   constants `DEBUG_STATS`, `DEBUG_COLLECTABLE`,
   `DEBUG_UNCOLLECTABLE`, `DEBUG_SAVEALL`, `DEBUG_LEAK`.
6. **Freeze:** `gc.freeze()`, `gc.unfreeze()`,
   `gc.get_freeze_count() -> Int`.
7. **Callbacks:** `gc.callbacks -> List[Block]` (mutable).

**Type discipline:** `Boolean`/`Int`/`Tuple`/`List` end-to-end.

**Out of scope (for v1):**

- `gc.get_objects(generation=None)`, `gc.get_referrers(*objs)`,
  `gc.get_referents(*objs)`, `gc.is_tracked(obj)`, `gc.is_finalized(obj)`
  — all introspection-heavy; clash with POOP's no-introspection rule.

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
| `os` | proposed | See proposal above |
| `io` | proposed | See proposal above |
| `time` | proposed | See proposal above |
| `logging` | proposed | See proposal above |
| `argparse` | out | POOP programs don't expose a CLI surface (yet) |
| `getpass` | covered | `getpass` namespace (shipped in v0.11.0) |
| `curses` | out | Terminal UI — niche |
| `platform` | proposed | See proposal above |
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
| `asyncio` | proposed | See proposal above |
| `socket` | proposed | See proposal above |
| `ssl` | proposed | See proposal above |
| `select` | out | Low-level — `selectors` is preferred |
| `selectors` | out | Low-level multiplexing |
| `signal` | proposed | See proposal above |

### Internet Data Handling

| Module | Status | Sketch |
|---|---|---|
| `email` | proposed | See proposal above |
| `json` | covered | `json` namespace (shipped in v0.25.0) |
| `mailbox` | out | Niche legacy |
| `mimetypes` | covered | `mimetypes` + `MimeTypes` (shipped in v0.15.0) |
| `base64` | covered | Methods on `Bytes` and `Str` (shipped in v0.13.0) |
| `binascii` | covered | `binascii` namespace (shipped in v0.14.0) |
| `quopri` | out | Niche legacy encoding |

### Structured Markup Processing Tools

| Module | Status | Sketch |
|---|---|---|
| `html` | proposed | See proposal above |
| `xml` | proposed | See proposal above |
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
| `unittest` | proposed | See proposal above |
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
| `profile` / `cProfile` / `pstats` | proposed | See proposal above |
| `timeit` | proposed | See proposal above |
| `trace` | out | Depends on introspection |
| `tracemalloc` | out | Depends on introspection |

### Python Runtime Services

| Module | Status | Sketch |
|---|---|---|
| `sys` | proposed | See proposal above |
| `sysconfig` | out | Build-time metadata |
| `builtins` | out | POOP *replaces* this |
| `warnings` | out | POOP doesn't have a warning concept |
| `dataclasses` | out | POOP classes don't use decorators |
| `contextlib` | covered | Reachable via `With` |
| `abc` | out | All POOP classes can be subclassed |
| `atexit` | proposed | See proposal above |
| `traceback` | out | Depends on introspection |
| `gc` | proposed | See proposal above |
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

