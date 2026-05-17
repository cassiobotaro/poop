# Code review findings — `poop/types/` + `poop/transformers/`

Output of the "Expert code review across `poop/types/` and `poop/transformers/`" proposal. Five parallel sub-agent reviews covered bugs, API consistency, boilerplate, test coverage, and transformer-init consistency.

The v0.54.1 fixes (3 bugs + platform-constants fix + `re.error` exposure + duplicate-binding guard test + CLAUDE.md `Random` entry) shipped. The rows below are the **active backlog** — every item is still pending. Pick one, fix it, drop the row.

## API consistency

| # | Severity | Location | Issue |
|---|---|---|---|
| A3 | Médio | `poop/types/xml.py:67,71`, `poop/types/logging.py:111`, `poop/types/ssl.py:77,85` | Setter-method drift — `Element.set_text/set_tail`, `Logger.set_propagate`, `SSLContext.set_check_hostname/set_verify_mode` violate the post-v0.54 convention "assignment, not setter methods". Collapse to `@property` + `@X.setter` pairs. Breaking — defer to next minor. |
| A4 | Médio | `poop/types/threading.py:224,231,243`, `poop/types/multiprocessing.py:171,179`, `poop/types/weakref.py:250` | 6 sites still use the inline `Wrapper.__new__(Wrapper); w._impl = x` anti-pattern. 12 other files use the canonical `_from_impl(cls, impl)` classmethod. Standardize. |

## Boilerplate consolidation

| # | Severity | Issue | Estimated LOC |
|---|---|---|---|
| C1 | Alto win | `_opt_int` / `_opt_str` / `_opt_timeout` / `_b` / `_i` redefined across ~25 files. `poop/types/_unwrap.py` already exists but is underused (12 cases of `_b` alone). Consolidate into the existing module. | -140 to -180 |
| C2 | Alto win | Pattern `if x is not None: kwargs["x"] = x._value` appears in 146 spots across 29 files (`subprocess`, `tarfile`, `shutil`, `zipfile`, `ssl`, `http`, `urllib`, `smtplib`, …). A `_kwargs_from(**named)` helper would shrink each 3-line block to 1 line. | -290 |
| C3 | Médio | Paired with A4 — extract a shared `_ImplWrapperMixin._from_impl` so the 12 existing classmethods + 6 inline sites share one declaration. | -30 to -40 |
| C4 | Baixo | `byte_array.py` has 9 function-local imports of `poop.types._unwrap` with no circular dependency — should be top-level. `int.py`/`float.py` have similar candidates. | -15 to -25 |
| C5 | Discutível | Heavy property-delegation blocks in `urllib`, `ipaddress`, `tarfile`, `sys`, `uuid` (16-32 properties each, all `return Str(self._impl.X)` shape). A `@_delegated_property(Str)` decorator could compress them but loses static-type inference, IDE jump-to-def, and per-property docstrings. | -150 to -300 (cosmetic) |

## Test coverage

The "55% bundled vs 99% isolated" claim from the original proposal was **folklore** — the supposed pytest-cov interaction does not exist. Running `pytest tests/test_types/test_sys.py --cov=poop.types.sys --cov-config=/dev/null` reports `poop/types/sys.py` at **99%**, identical to the bundled run. The confusion came from `--cov=poop` in `addopts`: when only one file is run, the TOTAL line includes every untouched module as 0%, dragging the aggregate to ~48%. Per-module % is stable.

| # | Severity | Issue |
|---|---|---|
| T1 | Baixo | ~7 of 60 validator test files don't assert on the `instead`/`use \`X\`` substitute hint via `match=`. Sweep the remaining files for consistency. |
| T2 | Médio | Top 10 worst-covered modules: `multiprocessing` (76%), `struct` (77%), `mimetypes` (80%), `weakref` (81%), `sqlite3` (82%), `repl` (84%), `ssl` (84%), `shutil` (84%), `timeit` (84%), `glob` (85%). Most misses are error paths uncovered by smoke tests. |
| T3 | Baixo | Only 2 test files use `Try(...)`; 8 `except_(` total. Integration tests don't exercise error paths through `Try.except_`. Pair with T2 — round-trip + Try.except_ tests per module. |
| FYI | — | Document the cov-config gotcha in CONTRIBUTING.md: "to measure a single module, use `--cov-config=/dev/null --cov=poop.types.X`". |

## Transformer init / namespace registry

| # | Severity | Issue |
|---|---|---|
| N1 | Baixo | 264 declared bindings, 0 collisions today. `tests/test_pipeline.py::test_no_duplicate_bindings_across_transformers` (v0.54.1) catches future collisions at startup. **Still pending**: refactor `DEFAULT_NAMESPACE = {...}` from 88 manual spreads to a loop over a declarative list (cosmetic, but `__init__.py` shrinks and grows linearly with future namespaces). |

## Out of scope (per proposal)

- Performance review.
- Adding new namespace wrappers.
- Rewriting the validator pipeline.
- Adding `mypy` alongside `ty`.

---

**Update the doc as items ship.** Drop the row once the fix lands; if a row partially ships, narrow the description to the remaining work.
