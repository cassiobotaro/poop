# Tasks

## 1. The tree passes ty 0.0.87 before the bump

- [x] 1.1 Annotate the eight `_eq_group` / `_order_group` overrides (`poop/types/_mapping.py`, `bytes.py` ×2, `byte_array.py` ×2, `frozen_set.py`, `memory_view.py`, `set.py`) as `ClassVar[str | None]`, matching the mixins' declaration; verify `uvx ty@0.0.87 check poop/ tests/ --output-format concise | grep -c invalid-mutable-override` prints `2`.
- [x] 1.2 In `poop/errors.py`, add `# ty: ignore[invalid-mutable-override]` with the reason (a validator always has a node, so `ValidationError` guarantees a position) to the `lineno` and `col_offset` declarations; verify the same grep prints `0`.
- [x] 1.3 In `poop/types/block.py`, bind the receiver through `partial(cast("Callable[..., R]", self), instance)` with a one-line comment; verify `uvx ty@0.0.87 check poop/ tests/` reports no `invalid-argument-type`, and `uv run pytest tests/test_types/test_block.py -q` passes.
- [x] 1.4 Change the return annotation of `_poop_errors` (`poop/cli.py`), `_recursion_budget` (`poop/executor.py`) and `_displaying_through` (`poop/repl.py`) from `Iterator[None]` to `Generator[None]`, adjusting each `collections.abc` import and removing `Iterator` where it becomes unused; verify `uvx ty@0.0.87 check poop/ tests/` reports no `deprecated` and `uv run ruff check` passes (no unused import).
- [x] 1.5 In `tests/test_types/test_sentinel.py`, replace `assert Sentinel(Str("")).print` with `assert str(Sentinel(Str(""))) == ""`, keeping the comment; verify `uv run pytest tests/test_types/test_sentinel.py -q` passes and `uvx ty@0.0.87 check poop/ tests/` prints `All checks passed!`.
- [x] 1.6 Run the full gate on the pinned toolchain, `uv run ruff check && uv run ruff format --check && uv run pytest`; verify every step exits 0. `uv run ty check` is expected to warn `ignore-comment-unknown-rule` on the two `errors.py` lines until 2.2 installs ty 0.0.87, which is why this group is committed together with group 2 in 2.3, not on its own.

## 2. Lock and floors

- [x] 2.1 Run `uv lock --upgrade` and verify the diff of `uv.lock` moves exactly typer, prek, ruff, ty, coverage, iniconfig and pygments to the versions the proposal lists, and nothing else.
- [x] 2.2 In `pyproject.toml`, raise the floors to the locked versions: `typer>=0.27.3`, `prek>=0.5.5`, `ruff>=0.17.0`, `ty>=0.0.87` (rich and pytest-cov unchanged); verify `uv lock` afterwards reports no further change and `uv sync --dev` installs the new versions (`uv run ruff --version` prints 0.17.0, `uv run ty --version` prints 0.0.87).
- [x] 2.3 Run `prek install` so the hooks use the synced `prek`, then the full gate `uv run ruff check && uv run ruff format --check && uv run ty check poop/ tests/ && uv run pytest`; verify every step exits 0 and coverage stays at or above 95%, then commit groups 1 and 2 together (code, `uv.lock`, `pyproject.toml`) as `chore(deps): bump typer, prek, ruff and ty; the tree is clean under the new ty` (hooks pass on this one commit; neither half passes them alone).

## 3. Push and housekeeping

- [x] 3.1 Push `main` and wait for the CI run of the push; verify both jobs (3.15, 3.15t) conclude `success` with `gh run view <id> --json jobs`.
- [x] 3.2 Close Dependabot pull requests #70, #77, #78 and #79 with `gh pr close <n> --comment "<reason>"`, the comment naming the superseding commit and that Dependabot's uv updater does not yet support Python 3.15; verify `gh pr list --author app/dependabot` is empty.

## Workflow follow-up

- Archive the change after the CI run is green; no spec sync, since it declares `skip_specs`.
- When Dependabot announces 3.15 support, its weekly `uv` run resumes with no change here.
