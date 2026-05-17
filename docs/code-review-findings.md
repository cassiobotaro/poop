# Code review findings — `poop/types/` + `poop/transformers/`

Active engineering backlog. v0.54.1 closed the bug fixes + alto convention violation. v0.54.2 closed a wave of refactor wins (C4, FYI, T1, A4, C3, N1 + partial C1). What remains:

## API consistency

| # | Severity | Location | Issue |
|---|---|---|---|
| A3 | Médio | `poop/types/xml.py:67,71`, `poop/types/logging.py:111`, `poop/types/ssl.py:77,85` | Setter-method drift — `Element.set_text/set_tail`, `Logger.set_propagate`, `SSLContext.set_check_hostname/set_verify_mode` violate the post-v0.54 convention "assignment, not setter methods". Collapse to `@property` + `@X.setter` pairs. Breaking — defer to next minor. |

## Boilerplate consolidation

| # | Severity | Issue | Estimated LOC |
|---|---|---|---|
| C1 | Médio (residual) | `_opt_int` / `_opt_str` / `_unwrap_str` / `_opt_path_arg` still redefined across ~10 files. Each carries a slightly different signature (Path-vs-Str unwrapping, optional return shape) and must be audited per call-site before centralising. The most-duplicated `_b`/`_opt_timeout` already moved to `_unwrap.py` in v0.54.2. | -60 to -100 |
| C4 | Baixo (residual) | Function-local `from poop.types._unwrap import _unwrap` calls still live in `bytes.py` (11), `string.py` (5), `path.py` (3), `random.py` (8), `secrets.py` (3), `binascii.py` (2), `hash.py`, `sqlite3.py`, `re.py`, `datetime.py`, `decimal.py`. v0.54.2 only hoisted `byte_array.py`/`int.py`/`float.py`. The remaining files need a per-module cycle audit before hoisting (each one *might* be a real cycle dodge). | -30 to -40 |
| C2 | Alto win | Pattern `if x is not None: kwargs["x"] = x._value` appears in 146 spots across 29 files (`subprocess`, `tarfile`, `shutil`, `zipfile`, `ssl`, `http`, `urllib`, `smtplib`, …). A `_kwargs_from(**named)` helper would shrink each 3-line block to 1 line. Mechanical sweep; needs care with the ~30 sites that also wrap values via `_impl` instead of `_value`. | -290 |
| C5 | Discutível | Heavy property-delegation blocks in `urllib`, `ipaddress`, `tarfile`, `sys`, `uuid` (16-32 properties each, all `return Str(self._impl.X)` shape). A `@_delegated_property(Str)` decorator could compress them but loses static-type inference, IDE jump-to-def, and per-property docstrings. | -150 to -300 (cosmetic) |

## Test coverage

The "55% bundled vs 99% isolated" claim was folklore (see CONTRIBUTING.md "Testing" section for the cov-config recipe). Real coverage gaps:

| # | Severity | Issue |
|---|---|---|
| T2 | Médio | Top 10 worst-covered modules: `multiprocessing` (76%), `struct` (77%), `mimetypes` (80%), `weakref` (81%), `sqlite3` (82%), `repl` (84%), `ssl` (84%), `shutil` (84%), `timeit` (84%), `glob` (85%). Most misses are error paths uncovered by smoke tests. |
| T3 | Baixo | Only 2 test files use `Try(...)`; 8 `except_(` total. Integration tests don't exercise error paths through `Try.except_`. Pair with T2 — round-trip + Try.except_ tests per module. |

## Out of scope (per proposal)

- Performance review.
- Adding new namespace wrappers.
- Rewriting the validator pipeline.
- Adding `mypy` alongside `ty`.

---

**Update the doc as items ship.** Drop the row once the fix lands; if a row partially ships, narrow the description to the remaining work.
