# Code review findings — `poop/types/` + `poop/transformers/`

Active engineering backlog. v0.54.1 closed the bug fixes + alto convention violation. v0.54.2 closed a wave of refactor wins (C4, FYI, T1, A4, C3, N1 + partial C1). What remains:

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
