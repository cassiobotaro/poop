# Proposals

## Audit every namespace signature against its Python counterpart

v0.51.0 fixed two cases of "POOP design diverged from Python without
a real reason": `args.list()`/`.script()`/`.rest()` collapsed back
into `sys.argv()`, and `process.pid()` / `env.get()` collapsed back
into `os.getpid()` / `os.environ.get()`. Both were proposed in
`proposals.md` as "POOP splits the module into focused namespaces"
and both turned out to be cosmetic indirection that broke the
Python→POOP intuition. With ~70 wrappers shipped between v0.6 and
v0.51, more of these are almost certainly hiding in the code.

This is a **shape audit**, not a feature audit. It complements the
"Expert code review" proposal (which targets bugs, helpers, and
test coverage) by asking only one question per method: *if a Python
user reaches for this, does the POOP form match what their fingers
expect?*

**Signature-shape drift to look for, category by category:**

1. **Methods renamed away from their Python original.**
   - `Sys.Stdout.writeln(s=none)` — there is no `writeln` in
     CPython's `sys.stdout`. The Python idiom is `print(x)` (which
     adds a newline) or `sys.stdout.write(x + "\n")`. Either keep
     `writeln` as a POOP-only convenience (and document so) or
     drop it.
   - `Logger.set_propagate(b)` — Python uses `logger.propagate =
     True` (attribute-set). POOP has to use a method; the question
     is whether the method should be `.set_propagate(b)` (POOP
     setter convention) or `.propagate_(b)` / `.propagate(b)`
     (closer to the attribute name). Decide one rule and apply it
     across `Logger.set_propagate`, `Element.set_text` /
     `set_tail`, `SSLContext.set_verify_mode` /
     `set_check_hostname`, etc.
   - `Atexit._run_exitfuncs()` / `Atexit._clear()` — the leading
     `_` mirrors `atexit._run_exitfuncs` (it's actually private in
     CPython). Fine; just confirm the underscore intent matches
     CPython's, not POOP convention.

2. **Sub-namespaces created where Python doesn't have one.**
   The v0.51.0 lesson — `args` / `process` / `env` were invented;
   Python doesn't ship them. Check every existing sub-namespace
   against its CPython parent:
   - `email.utils` — exists in CPython ✓
   - `email.policy` — exists in CPython ✓
   - `pstats.SortKey` — exists in CPython ✓
   - `html.entities` — exists in CPython ✓
   - `html.parser` — POOP exposes `HTML.parser` as the
     `HTMLParser` class itself, not as a sub-namespace. Python's
     `html.parser` is a module; the class is `html.parser.HTMLParser`.
     Audit whether `HTML.parser` resolving to the class (not a
     submodule with the class inside) surprises users.
   - `os.environ` — exists in CPython ✓ (v0.51.0)
   - `ET.etree` / `XML.ET` — POOP exposes `XML.ET = ET`. Python's
     attribute path is `xml.etree.ElementTree.ET`. Audit.

3. **Parameter names changed from CPython's.**
   - `Logging.basicConfig(level=none, fmt=none)` — Python's
     `logging.basicConfig` parameter is `format`, not `fmt`. POOP
     renames it to avoid shadowing the `format` builtin, but POOP
     has banned that builtin via the `no_format` validator —
     there's no longer a reason to rename.
   - `Formatter(fmt=...)` — same `fmt` vs `format` divergence.
     Python's `logging.Formatter.__init__` first positional is
     `fmt` (so this one's actually right).
   - Every wrapper that built `kwargs["x"] = x._value` for
     optional kwargs — check the POOP-side keyword spelling
     against the Python original.

4. **Required-vs-optional mismatch.**
   - `Subprocess.run` accepts everything as optional (`capture_output=none`,
     `check=none`, etc.). Python's `run` is positional-only on `args`
     and the rest are kwargs with `False` / `None` defaults. POOP
     widened many defaults to `none` — semantically identical for
     bool flags but **breaks** for flags that distinguish "not
     passed" from `False` in CPython. Inventory each `none`-defaulted
     kwarg in `subprocess`, `socket`, `ssl`, `asyncio`, `logging`,
     `multiprocessing`, `concurrent`, and `subprocess` against the
     real CPython default.

5. **Methods exposed as callables when Python exposes attributes.**
   POOP's design forces zero-arg methods where Python uses
   attributes (`sys.argv()` not `sys.argv`, since POOP is
   method-message-passing). That's by design. But the boundary
   between "wrap as method" and "wrap as `@property`" has drifted:
   - `Element.tag` / `.text` / `.tail` / `.attrib` are
     `@property` (no call needed). Why are these properties when
     `sys.argv()` is a method?
   - `EmailMessage.is_multipart()` is a method (matches Python's
     method shape — `is_multipart` is `def`).
   - `Stats.print_stats()` is a method (matches Python).
   - `Time.tzname()` is a method, but Python's `time.tzname` is a
     module-level **attribute** (tuple). Symmetric to `sys.argv`.
   The rule should be: **POOP attributes → properties; POOP
   methods → methods**. Apply uniformly. (v0.51.0 picked
   "everything is a method" for `sys`/`os` — confirm the same
   rule applies elsewhere or document the exception.)

6. **Return shapes that aren't quite Python's.**
   - `Profile.print_stats()` returns `Str` (captured) instead of
     writing to stdout. Python's `print_stats` prints + returns
     `Stats`. POOP changed the contract for the reasonable goal
     of making the output capturable, but it diverges from
     Python — flag and decide.
   - `Stats.sort_stats(*keys) -> Stats` returns `self` for
     chaining (matches Python ✓).
   - Methods returning `none` where Python returns the object for
     chaining (or vice-versa) — audit each.

7. **Type narrowing on returns.**
   - `Sys.implementation()` / `.flags()` / `.float_info()` /
     `.int_info()` / `.hash_info()` / `.thread_info()` all return
     raw CPython named-tuples (typed `Any`). Either wrap each as
     a POOP record, or expose specific accessors
     (`Sys.version_info().major` etc), but don't bridge half-way.
   - `Asyncio.get_event_loop()` returns the raw Python loop
     untyped. POOP user code holding the loop has no message
     surface to send.

8. **Convention drift in identifier casing.**
   The `feedback_constants_uppercase.md` memory says POOP follows
   Python's exact casing per source module. Audit:
   - `signal.SIGINT` (uppercase, matches Python ✓)
   - `errno.EPERM` (uppercase, matches Python ✓)
   - `math.pi` (lowercase, matches Python ✓)
   - `Concurrent.FIRST_COMPLETED` — Python's
     `concurrent.futures.FIRST_COMPLETED` is uppercase ✓
   - `Concurrent.Future` (the class) vs `CFFuture` (the binding) —
     Python is just `Future`. POOP renamed to disambiguate from
     `asyncio.Future`. Audit whether the rename pays off or just
     surprises Python users; consider exposing only
     `concurrent.Future` and dropping the top-level `CFFuture`
     name.

**Methodology — how to actually do the audit:**

For each module wrapper in `poop/types/`:

1. Open CPython's docs page for the same module in a tab.
2. Walk the CPython public surface top to bottom. For each name:
   - Find the POOP counterpart (or note "not exposed").
   - If exposed: confirm name, parameter list, default values,
     return type, attribute-vs-method match Python.
3. Record divergences in a triage table with columns:
   `module | python | poop | reason for divergence | keep / fix`.
4. For each `fix` row, open an issue or a small PR.

Cross-cut: grep for the `set_` prefix across all wrappers and decide
the project-wide rule for property-setter equivalents.

**Type discipline / scope:**

- **Public method signatures only.** Internal helpers
  (`_unwrap_args`, `_opt_path`, etc.) are not part of the contract.
- **Behavioral divergence is allowed when POOP semantics demand it**
  (e.g., `subscript → .at()`, `print → .print()`, `iteration → .do`).
  Document each sanctioned divergence in `INFECTIONS.md` § "Active
  infections" so it's not re-flagged on the next audit.
- **Memory `feedback_python_mirror.md` is the rule of thumb:** when
  Python and POOP shapes diverge without a banned-construct excuse,
  prefer the Python shape.

**Out of scope (for v1):**

- Wholesale rename to match CPython's snake_case where Python uses
  camelCase by accident (e.g., `logging.basicConfig`). Keep
  Python's actual spelling — `basicConfig`, `assertEqual` — even
  when Python is the inconsistent one.
- Argument-order changes that would break v0.5x callers — queue
  for v0.6.0 with a deprecation cycle.
- Adding new exposed APIs — this audit only re-aligns what's
  already wrapped.
- Re-litigating the v0.51.0 decisions (`sys.argv()`, `os.getpid()`,
  `os.environ.*`) — those are settled.

## Expert code review across `poop/types/` and `poop/transformers/`

The codebase doubled in size during v0.43→v0.51 (now ~21k LOC across
`poop/types/` + `poop/transformers/`, with ~70 namespace wrappers
each in the 50-300 LOC range). The wrappers were scaffolded fast —
proposal → code → tests → docs → ship, one batch per minor version —
and the rapid cadence likely left bugs, drift, and easy-to-spot
refactor opportunities that an outside Python expert would flag in
their first careful read. Project coverage sits at ~55% in the
bundled test run; the test suites are constructor-and-shape heavy
and rarely exercise edge cases.

**What a reviewer should hunt for, in priority order:**

1. **Latent bugs in `_value` / `_impl` unwrap paths.**
   - `x._value` access without `isinstance` guards on union-typed
     parameters (e.g., a method declared `Path | Str` that calls
     `.value` on a `Path` instance).
   - `none` vs Python `None` mix-ups — POOP `NoneClass` is its own
     thing; `is None` checks against POOP-typed inputs silently miss.
   - Bytes-vs-Str confusion in modules that can return either
     (`subprocess.run` with/without `text=`, `email.get_content`,
     `ET.tostring` with/without `encoding=`). The wrappers branch on
     `isinstance(result, bytes)` — confirm every code path.
   - Forwarding `_impl.method(*args)` without unwrapping POOP args
     (or double-wrapping return values).

2. **API-shape inconsistencies across wrappers.**
   - `__slots__` is present in some `Object` subclasses
     (`Stats`, `Profile`, `EmailMessage`) and absent in others —
     should be uniform.
   - Some classes attach `__test__ = False` to dodge pytest
     collection (`TestCase`, `TestSuite`, `TestRunner`,
     `TestResult`); the same precaution may be missing on other
     `Test*` / `Helper*` named POOP classes if any exist.
   - Mixing `@property` + setter-method (`SSLContext.verify_mode`
     getter + `.set_verify_mode(m)` setter) vs straight method-pair
     (`Logger.propagate` + `.set_propagate(b)`) vs property-only
     (`Element.tag` / `.text` / `.tail`). Pick one convention for
     "Python attribute → POOP" and apply uniformly.
   - Error-class exposure: some namespaces expose every error class
     (`subprocess.SubprocessError` / `CalledProcessError` /
     `TimeoutExpired`), others expose only the top one
     (`json.JSONDecodeError`), others none. A consistent rule:
     "expose anything user code might pass to `Try.except_`".
   - Constants: `socket.AF_UNIX` binds to `none` when the platform
     doesn't have it; `signal.SIGUSR1` does the same; `resource`
     does the same; but some other modules raise on missing
     attributes. Pick one fallback rule.

3. **Repeated boilerplate that should become shared helpers.**
   - `_opt_str(x)` / `_opt_path(x)` / `_opt_timeout(x)` /
     `_unwrap_args(x)` helpers are redefined in `csv.py`,
     `configparser.py`, `email.py`, `xml.py`, `subprocess.py`,
     `multiprocessing.py`, `threading.py`, `concurrent.py`,
     `queue.py`, `ssl.py`, `socket.py`, `profile.py`, `signal.py`,
     `time.py`, `os.py`. Move to a single `poop/types/_unwrap.py`.
   - The kwargs-builder pattern `if x is not None: kwargs["x"] =
     x._value` appears in dozens of methods. A `_build_kwargs(...)`
     helper or a small builder DSL would dedupe ~200 LOC.
   - `true if cond else false` is used in some places while
     `Boolean.from_(cond)` exists in others — settle on one.
   - The `Wrapper.__new__(Wrapper); wrapper._impl = py_obj` pattern
     (in `Multiprocessing.current_process`, `Threading.enumerate`,
     etc.) bypasses `__init__` to wrap an existing Python object.
     A `Wrapper._from_impl(py_obj)` classmethod would make this
     intent explicit and uniform.

4. **Type-discipline drift.**
   - Methods declared as taking POOP types (`Str`, `Int`, `Path`)
     that silently accept Python strings/ints/paths via duck-typing
     because they only call `._value` after an `isinstance`. The
     memory note `feedback_poop_signatures.md` says public methods
     on POOP types should annotate POOP types only — audit for
     signatures that widened to accept Python primitives.
   - Return types like `Any` where a real POOP union exists.
     Particularly `_modules_dict`, `Sys.implementation`,
     `Sys.flags`, etc. — opaque Python objects flow through to
     POOP user code uncasted.

5. **Test-suite coverage gaps and anomalies.**
   - 55% total coverage when running the full suite vs ~99% when
     running each `test_X.py` alone — there's a pytest-cov
     interaction we noted but never investigated (probably tests
     re-importing modules between runs). Worth root-causing.
   - Many namespace test files only verify "constructor returns
     instance" + "static method returns expected POOP type" but
     never round-trip data through the wrapped operation. E.g.,
     `pickle.dumps` / `pickle.loads` may not be tested with non-
     trivial inputs.
   - Interpreter-integration smoke tests use only the happy path —
     no `Try.except_` paths, no validator-rejection paths.

6. **`poop/transformers/__init__.py` consistency.**
   - The `NAMESPACE` dicts contributed by each transformer module
     are merged in `DEFAULT_NAMESPACE` via repeated `**_x_namespace`
     spreads — a long, manual list (~70 entries). One bad order
     causing a silent key collision is plausible; switching to a
     loop over a `[(name, mod)]` list would catch dupes at startup.
   - The bindings list documented in `CLAUDE.md` may have drifted
     from what's actually in `DEFAULT_NAMESPACE`. A self-test that
     diffs the live dict against the doc list would catch this.

7. **Docs drift between `INFECTIONS.md` / `MIGRATION.md` /
   `proposals.md` / `CLAUDE.md`.**
   - INFECTIONS now has ~2300 lines of tables. Many entries
     describe pre-refactor APIs (e.g., the v0.51 refactor moved
     `args.*` → `sys.argv()` but a casual reader would still see
     the table-row "`args.list()` / `args.rest()`"). A grep for
     terms removed in v0.51 (`args.`, `process.`, `env.`) across
     all docs should find no hits.
   - `INFECTIONS.md`'s "Stdlib coverage" tables are stale
     whenever a module gets surfaced or skipped — every namespace PR
     should update them in the same commit.

**Methodology — how to actually do the review:**

- Read `poop/types/` in two passes:
  1. **First pass:** open every wrapper file and skim
     `__init__` / public methods / `_impl` access patterns. Note
     anything that differs from the file's neighbours.
  2. **Second pass:** for each `class X(Object)`, confirm the
     wrapper exposes everything its CPython counterpart exposes
     (cross-reference `dir()` of the underlying module). Flag
     anything missing or anything we added that CPython doesn't
     have.
- Run `coverage report --sort=miss` and triage the 100 worst-
  covered modules: most should get a 5-line `# fixed-input
  round-trip` test, not a full property-test buildout.
- For each `_unwrap`/`_wrap`/`_opt_X` helper: find all duplicates
  via `git grep`, settle on one canonical home, replace.

**Type discipline / scope:**

- **One issue per fix.** Don't bundle "rename `_value` → `value`"
  with "tighten union types" — they trigger different blast radii.
- **Maintain backward compatibility within `v0.5x`.** If a fix
  requires changing a public method signature, queue it for the
  next breaking minor (`v0.6.0`); silent fixes (helper extraction,
  type narrowing, added tests) ship as patch releases.
- **Output:** a triaged checklist of findings (issue per bug,
  PR per refactor) rather than a single mega-PR.

**Out of scope (for v1):**

- Performance review — POOP is not optimized for production use,
  and the message-dispatch overhead is a known design cost.
- Adding new namespace wrappers — only fix what's there.
- Rewriting the validator pipeline — separate concern, separate
  proposal.
- Adding `mypy` alongside `ty` — both check the same things; pick
  one (currently `ty`) and stop.

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

