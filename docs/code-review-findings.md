# Code review findings — `poop/types/` + `poop/transformers/`

Output of the "Expert code review across `poop/types/` and `poop/transformers/`" proposal. Five parallel sub-agent reviews covering bugs, API consistency, boilerplate, test coverage, and transformer-init consistency. Findings ranked by severity; the "Decision" column tracks whether each item shipped, was deferred, or was confirmed OK-as-is.

The fixes shipped against this doc landed in v0.54.1 (patch-compatible) and follow-up PRs. Anything still `defer` is the live backlog.

## Bugs (latent behavior errors)

| # | Severity | Location | Issue | Decision |
|---|---|---|---|---|
| B1 | Médio | `poop/types/email.py:37-45` | `EmailMessage.set_content(Bytes(b"x"), Str("plain"))` raises `TypeError: set_bytes_content() missing 1 required positional argument: 'maintype'`. Branches for `Bytes` and `Str` are functionally identical and both miss `maintype` for bytes. | **fix in v0.54.1** |
| B2 | Médio | `poop/types/email.py:47-51` | `EmailMessage.get_content()` returns garbage `Str("<email.message.EmailMessage ...>")` for multipart messages — falls through to `Str(result)` regardless of the underlying type. | **fix in v0.54.1** |
| B3 | Baixo | `poop/types/socket.py:25-38` | `_wrap_address` only handles `tuple` and `str`; AF_UNIX abstract-namespace `bytes` addresses are returned raw, leaking a Python type and violating the declared `-> Tuple \| Str` return. | **fix in v0.54.1** |

## API consistency

| # | Severity | Location | Issue | Decision |
|---|---|---|---|---|
| A1 | **Alto** | `poop/types/signal.py:19-21,59-67`, `poop/types/socket.py:158-160`, `poop/types/resource.py:90-94` | Platform-specific constants fall back to Python `None` instead of POOP `none`. Breaks the documented "Platform-specific constants" convention (`.is_none()` is uniformly callable). | **fix in v0.54.1** |
| A2 | Médio | `poop/types/re.py` | `re.error` exception class is not exposed — POOP user code can't `Try.except_(re.error, ...)`. Other namespaces (`json.JSONDecodeError`, `sqlite3.OperationalError`, etc.) follow the rule. | **fix in v0.54.1** |
| A3 | Médio | `poop/types/xml.py:67,71`, `poop/types/logging.py:111`, `poop/types/ssl.py:77,85` | Setter-method drift — `Element.set_text/set_tail`, `Logger.set_propagate`, `SSLContext.set_check_hostname/set_verify_mode` all violate the post-v0.54 convention "assignment, not setter methods". Should collapse to `@property` + `@X.setter` pairs. | **defer v0.55** (breaking) |
| A4 | Médio | `poop/types/threading.py:224,231,243`, `poop/types/multiprocessing.py:171,179`, `poop/types/weakref.py:250` | 6 sites still use the inline `Wrapper.__new__(Wrapper); w._impl = x` anti-pattern. 12 other files use the canonical `_from_impl(cls, impl)` classmethod. Standardize. | **defer v0.55** |
| A5 | Baixo | `poop/transformers/__init__.py` | Manual `**_X_namespace` spreads (88 of them) provide zero protection against silent key collisions if a future PR redefines an existing name. 0 collisions today. | **fix in v0.54.1** (declarative loop + guard test) |
| A6 | Baixo | `CLAUDE.md:61` | PascalCase enumeration of bindings is missing `Random` (per the project rule "a module that also exposes a class binds both names"). | **fix in v0.54.1** |
| OK1 | — | every `class X(Object)` | `__slots__` present uniformly across all Object subclasses. | confirmed OK |
| OK2 | — | `poop/types/unittest.py` | `__test__ = False` correctly set on `TestCase`, `TestSuite`, `TestRunner`, `TestResult`. No other `Test*`/`Suite*`/`Runner*` candidates exist. | confirmed OK |
| OK3 | — | namespace-wide | `true if cond else false` ternary used uniformly (213 occurrences); no `Boolean.from_(...)` helper introduced. Idiomatic, no churn. | confirmed OK |

## Boilerplate consolidation

| # | Severity | Issue | Estimated LOC | Decision |
|---|---|---|---|---|
| C1 | Alto win | `_opt_int` / `_opt_str` / `_opt_timeout` / `_b` / `_i` redefined across ~25 files. `poop/types/_unwrap.py` already exists but is underused (12 cases of `_b` alone). Consolidate into the existing module. | -140 to -180 | **defer** (large refactor; standalone PR) |
| C2 | Alto win | Pattern `if x is not None: kwargs["x"] = x._value` appears in 146 spots across 29 files (`subprocess`, `tarfile`, `shutil`, `zipfile`, `ssl`, `http`, `urllib`, `smtplib`, …). A `_kwargs_from(**named)` helper would shrink each 3-line block to 1 line. | -290 | **defer** (touches 29 files; standalone PR) |
| C3 | Médio | Cleanup of inline `Wrapper.__new__` (A4 above) is also part of this bucket — extract a shared `_ImplWrapperMixin._from_impl` so the 12 existing classmethods + 6 inline sites share one declaration. | -30 to -40 | **defer v0.55** (paired with A4) |
| C4 | Baixo | `byte_array.py` has 9 function-local imports of `poop.types._unwrap` with no circular dependency — should be top-level. `int.py`/`float.py` have similar candidates. | -15 to -25 | **defer** |
| C5 | Discutível | Heavy property-delegation blocks in `urllib`, `ipaddress`, `tarfile`, `sys`, `uuid` (16-32 properties each, all `return Str(self._impl.X)` shape). A `@_delegated_property(Str)` decorator could compress them but loses static-type inference, IDE jump-to-def, and per-property docstrings. | -150 to -300 (cosmetic) | **discuss** (high ergonomic cost) |

## Test coverage

The "55% bundled vs 99% isolated" claim from the original proposal was **folklore** — the supposed pytest-cov interaction does not exist. Running `pytest tests/test_types/test_sys.py --cov=poop.types.sys --cov-config=/dev/null` reports `poop/types/sys.py` at **99%**, identical to the bundled run. The confusion came from `--cov=poop` in `addopts`: when only one file is run, the TOTAL line includes every untouched module as 0%, dragging the aggregate to ~48%. Per-module % is stable.

| # | Severity | Issue | Decision |
|---|---|---|---|
| T1 | Médio | None of the 33 validator test files asserts on the `instead`/`use \`X\`` substitute hint in error messages — 48 validators include the substitute, all silently editable. | **fix in v0.54.1** |
| T2 | Médio | Top 10 worst-covered modules: `multiprocessing` (76%), `struct` (77%), `mimetypes` (80%), `weakref` (81%), `sqlite3` (82%), `repl` (84%), `ssl` (84%), `shutil` (84%), `timeit` (84%), `glob` (85%). Most misses are error paths uncovered by smoke tests. | **defer** (round-trip + Try.except_ tests per module) |
| T3 | Baixo | Only 2 test files use `Try(...)`; 8 `except_(` total. Integration tests don't exercise error paths through `Try.except_`. | **defer** (paired with T2) |
| FYI | — | Document the cov-config gotcha in CONTRIBUTING.md: "to measure a single module, use `--cov-config=/dev/null --cov=poop.types.X`". | **defer** (CONTRIBUTING update) |

## Transformer init / namespace registry

| # | Severity | Issue | Decision |
|---|---|---|---|
| N1 | Baixo | 264 declared bindings, 0 collisions today, but the manual spread offers no protection. Refactor `DEFAULT_NAMESPACE = {...}` to a loop over a declarative list that raises on collision. Pair with a `tests/test_pipeline.py` guard. | **fix in v0.54.1** |
| N2 | Cosmético | Imports alphabetical (good), spreads append-only (acceptable, since order doesn't matter once collisions are forbidden). | OK |

## Out of scope (per proposal)

- Performance review.
- Adding new namespace wrappers.
- Rewriting the validator pipeline.
- Adding `mypy` alongside `ty`.

---

**This doc is the live backlog.** Cross-reference issue/PR numbers when each `defer` row is picked up. Drop rows once a fix lands.
